#!/usr/bin/env python3
"""
Turn the cell-averaged bathymetry from remap_bathymetry.py into the MITgcm
bathymetry for the Mediterranean + Black Sea configuration.

All edits are given in lon/lat (except the Atlantic open-boundary cut, which is
tied to the OBCS indices and therefore kept in grid indices). No random noise:
the output is identical every time the script is run.

Steps
  1. land/sea from the interpolation (wet_fraction >= threshold used there)
  2. cut the Atlantic to the open-boundary box
  3. force chosen islands to land, close chosen inlets
  4. route each strait along its real path (least-cost path through cells that
     contain water, forced through way-points) and set its depth
  5. keep only water connected to the Mediterranean / Black Sea
  6. remove one-cell dead-end inlets (strait cells protected)
  7. apply a minimum depth
  8. diagnostics: sill depth of each strait, faces of the strait channels
  9. write BATHYMETRY.nc (with mask), BATHYMETRY.bin, maskrbcs.bin, mask.nc

Usage:  python zero_out.py [interpolated.nc] [BATHYMETRY.nc]
"""

import heapq
import os
import sys

import numpy as np
from netCDF4 import Dataset
from scipy import ndimage

# ============================================================== settings
IFILE = sys.argv[1] if len(sys.argv) > 1 else "MIT_BATHY.nc"
OFILE = sys.argv[2] if len(sys.argv) > 2 else "BATHYMETRY.nc"
INPUT_DIR = "../input"              # where MITgcm reads its binaries
RBCS_NC = "maskrbcs.nc"             # updated if present
FACES_FILE = "strait_faces.txt"

MIN_DEPTH = 5.0                     # m; r* + 1 m top levels cope with this
OPEN_SEA_FRACTION = 0.9             # strait cells wetter than this keep their depth

# Atlantic: keep only the box feeding the western open boundary (grid indices,
# same as the original script so that data.obcs stays valid).
ATLANTIC_CUTS = [
    (slice(0, 25), slice(0, 62)),
    (slice(130, None), slice(0, 62)),
]

# Points inside the basins we keep (everything not connected to them is removed).
SEEDS = {"Mediterranean": (18.0, 34.0), "Black Sea": (34.0, 43.0)}

# Small islands wanted as one land cell (lon, lat of the island).
ISLANDS = {
    "Lampedusa": (12.59, 35.51),
    "Capri":     (14.24, 40.55),
    "Ponza":     (12.96, 40.90),
    "Giglio":    (10.90, 42.36),
    "Elba":      (10.25, 42.78),
}

# Cells to force to land (lon, lat), e.g. lagoon mouths. Disconnected lagoons
# (Amvrakikos, Kalloni, Novigrad/Posedarje, Bou Grara, Dnieper-Bug liman,
# Sivash, ...) are removed automatically by the connectivity step.
CLOSE = {
}

# Straits. 'path': way-points from one basin to the other, following the real
# channel. 'depth': "thalweg" (deepest source pixel, used on every path cell
# that is not open sea) or a number (used only on cells that were land). 'clip': (min, max) applied to the strait depths, None = no
# limit. Depths are positive metres.
STRAITS = {
    "Dardanelles": dict(
        path=[(26.10, 40.00), (26.33, 40.09), (26.42, 40.17),
              (26.60, 40.32), (26.69, 40.40), (26.95, 40.50)],
        depth="thalweg", clip=(50.0, None)),       # EMODnet thalweg >= 52 m
    "Bosphorus": dict(
        path=[(28.95, 40.95), (29.00, 41.03), (29.09, 41.12), (29.10, 41.28)],
        depth="thalweg", clip=(35.0, None)),      # southern sill ~32-35 m
    "Rion-Antirrion": dict(
        path=[(21.60, 38.27), (21.78, 38.31), (22.04, 38.32)],
        depth=62.0, clip=(62.0, None)),           # sill ~62 m
    "Oreoi": dict(
        path=[(22.95, 38.80), (23.07, 38.97), (23.12, 39.10)],
        depth="thalweg", clip=(None, None)),
}

# Strait sills reported at the end (two points, one on each side).
SILL_CHECKS = {
    "Gibraltar":   [(-6.8, 36.0), (-4.5, 36.2)],
    "Sicily":      [(11.0, 38.0), (13.0, 36.0)],
    "Otranto":     [(19.0, 41.8), (19.0, 39.3)],
    "Dardanelles": [(25.95, 40.0), (27.5, 40.7)],
    "Bosphorus":   [(28.6, 40.85), (29.6, 41.6)],
    "Kerch":       [(36.6, 44.85), (36.9, 45.8)],
}

# ============================================================== helpers
R_EARTH = 6371.0e3


def nearest(lon, lat, lo, la):
    d = (lon - lo) ** 2 * np.cos(np.radians(la)) ** 2 + (lat - la) ** 2
    return np.unravel_index(np.argmin(d), lon.shape)


def least_cost_path(cost, a, b):
    """Dijkstra on a 4-connected grid; cost is paid on entering a cell."""
    ny, nx = cost.shape
    dist = np.full(cost.shape, np.inf)
    prev = -np.ones(cost.shape + (2,), dtype=int)
    dist[a] = 0.0
    heap = [(0.0, a)]
    while heap:
        d, (j, i) = heapq.heappop(heap)
        if (j, i) == b:
            break
        if d > dist[j, i]:
            continue
        for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            jj, ii = j + dj, i + di
            if 0 <= jj < ny and 0 <= ii < nx:
                nd = d + cost[jj, ii]
                if nd < dist[jj, ii]:
                    dist[jj, ii] = nd
                    prev[jj, ii] = (j, i)
                    heapq.heappush(heap, (nd, (jj, ii)))
    path, c = [], b
    while c != a:
        path.append(c)
        c = tuple(prev[c])
        if c[0] < 0:
            raise RuntimeError("no path found")
    path.append(a)
    return path[::-1]


def sill_depth(depth, a, b):
    """Deepest depth at which a and b are still connected (minimax path)."""
    if depth[a] <= 0 or depth[b] <= 0:
        return None
    levels = np.unique(depth[(depth > 0) & (depth <= min(depth[a], depth[b]))])
    lo, hi = 0, len(levels) - 1
    best = None
    while lo <= hi:                       # binary search on the threshold
        mid = (lo + hi) // 2
        lab, _ = ndimage.label(depth >= levels[mid])
        if lab[a] > 0 and lab[a] == lab[b]:
            best = levels[mid]
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def spacing(lon, lat, j, i, axis):
    """Approximate face length (m) of the face shared with the next cell along axis."""
    if axis == 1:   # U face between (j,i-1) and (j,i): length ~ dy
        j2, i2 = min(j + 1, lon.shape[0] - 1), i
        j1 = max(j2 - 1, 0)
        return R_EARTH * np.hypot(np.radians(lat[j2, i2] - lat[j1, i2]),
                                  np.radians(lon[j2, i2] - lon[j1, i2]) * np.cos(np.radians(lat[j, i])))
    i2 = min(i + 1, lon.shape[1] - 1)
    i1 = max(i2 - 1, 0)
    return R_EARTH * np.hypot(np.radians(lat[j, i2] - lat[j, i1]),
                              np.radians(lon[j, i2] - lon[j, i1]) * np.cos(np.radians(lat[j, i])))


# ============================================================== read
with Dataset(IFILE) as src:
    lon = np.asarray(src["lon"][:], dtype=np.float64)
    lat = np.asarray(src["lat"][:], dtype=np.float64)
    elev = np.asarray(src["elevation"][:], dtype=np.float64)
    wf = np.asarray(src["wet_fraction"][:], dtype=np.float64)
    dmax = np.asarray(src["depth_max"][:], dtype=np.float64)
    gatts = {k: src.getncattr(k) for k in src.ncattrs()}

depth = np.where(elev < 0.0, -elev, 0.0)
edited = np.zeros(depth.shape, dtype=np.uint8)   # 1 island/close, 2 strait, 3 floor
protect = np.zeros(depth.shape, dtype=bool)

# ============================================================== 2. Atlantic
for sj, si in ATLANTIC_CUTS:
    depth[sj, si] = 0.0

# ============================================================== 3. islands / closures
for name, (lo, la) in {**ISLANDS, **CLOSE}.items():
    j, i = nearest(lon, lat, lo, la)
    if depth[j, i] > 0:
        depth[j, i] = 0.0
        edited[j, i] = 1
    print(f"land   {name:12s} [{j},{i}]  {lon[j, i]:.2f}E {lat[j, i]:.2f}N")

# ============================================================== 4. straits
faces = []
for name, s in STRAITS.items():
    pts = [nearest(lon, lat, lo, la) for lo, la in s["path"]]
    js = [p[0] for p in pts]
    is_ = [p[1] for p in pts]
    j0, j1 = max(min(js) - 4, 0), min(max(js) + 5, depth.shape[0])
    i0, i1 = max(min(is_) - 4, 0), min(max(is_) + 5, depth.shape[1])
    cost = 1.0 / (wf[j0:j1, i0:i1] + 0.01)     # land cells (wf=0) cost 100
    path = []
    for a, b in zip(pts[:-1], pts[1:]):
        seg = least_cost_path(cost, (a[0] - j0, a[1] - i0), (b[0] - j0, b[1] - i0))
        seg = [(j + j0, i + i0) for j, i in seg]
        path += seg if not path else seg[1:]

    lo_c, hi_c = s["clip"]
    print(f"strait {name}: {len(path)} cells")
    for j, i in path:
        protect[j, i] = True
        const = s["depth"] != "thalweg"
        if depth[j, i] > 0 and (const or wf[j, i] >= OPEN_SEA_FRACTION):
            new = depth[j, i]           # keep existing water; clip still applies
        else:
            new = dmax[j, i] if s["depth"] == "thalweg" else float(s["depth"])
        if lo_c is not None:
            new = max(new, lo_c)
        if hi_c is not None:
            new = min(new, hi_c)
        if new != depth[j, i]:
            edited[j, i] = 2
        print(f"   [{j},{i}] {lon[j, i]:6.2f}E {lat[j, i]:5.2f}N  wf {wf[j, i]:.2f}"
              f"  {depth[j, i]:6.1f} -> {new:6.1f} m")
        depth[j, i] = new
    for (ja, ia), (jb, ib) in zip(path[:-1], path[1:]):
        if ja == jb:   # zonal step: U point at max(i)
            jf, if_ = ja, max(ia, ib)
            faces.append((name, "U", jf, if_, spacing(lon, lat, jf, if_, 1),
                          min(depth[ja, ia], depth[jb, ib])))
        else:          # meridional step: V point at max(j)
            jf, if_ = max(ja, jb), ia
            faces.append((name, "V", jf, if_, spacing(lon, lat, jf, if_, 0),
                          min(depth[ja, ia], depth[jb, ib])))

# ============================================================== 5/6. connectivity + dead ends
def keep_connected(depth):
    lab, n = ndimage.label(depth > 0)
    keep = {lab[nearest(lon, lat, lo, la)] for lo, la in SEEDS.values()} - {0}
    removed = []
    for c in range(1, n + 1):
        if c not in keep:
            jj, ii = np.where(lab == c)
            removed.append((len(jj), lon[jj, ii].mean(), lat[jj, ii].mean()))
    return np.where(np.isin(lab, list(keep)), depth, 0.0), removed


depth, removed = keep_connected(depth)
print(f"\nremoved {len(removed)} disconnected water bodies "
      f"({sum(r[0] for r in removed)} cells); largest:")
for n, lo, la in sorted(removed, reverse=True)[:12]:
    print(f"   {n:4d} cells near {lo:6.2f}E {la:5.2f}N")

n_dead = 0
while True:
    wet = depth > 0
    p = np.pad(wet, 1, mode="edge")          # domain edge counts like its neighbour
    nland = 4 - (p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:])
    dead = wet & (nland >= 3) & ~protect
    if not dead.any():
        break
    n_dead += dead.sum()
    depth[dead] = 0.0
depth, removed2 = keep_connected(depth)
print(f"removed {n_dead} dead-end cells, then {len(removed2)} newly isolated bodies")

# ============================================================== 7. minimum depth
floor = (depth > 0) & (depth < MIN_DEPTH)
edited[floor & (edited == 0)] = 3
depth[floor] = MIN_DEPTH
print(f"minimum depth {MIN_DEPTH} m applied to {floor.sum()} cells")

wet = depth > 0
lab, n = ndimage.label(wet)
assert n == 1, f"ocean is split into {n} pieces - check straits"

# ============================================================== 8. diagnostics
print("\nsill depths (deepest connecting level):")
for name, (a, b) in SILL_CHECKS.items():
    s = sill_depth(depth, nearest(lon, lat, *a), nearest(lon, lat, *b))
    print(f"   {name:12s} {'not connected' if s is None else f'{s:7.1f} m'}")

with open(FACES_FILE, "w") as f:
    f.write("# Velocity faces along the hand-routed straits.\n"
            "# j,i are 1-based (Fortran) indices of the U or V point.\n"
            "# Flow through a U face uses dyG(i,j); through a V face dxG(i,j).\n"
            "# width_m is approximate; check against your grid files.\n"
            "# strait  type  j  i  width_m  depth_m\n")
    for name, t, j, i, w, d in faces:
        f.write(f"{name:16s} {t} {j + 1:4d} {i + 1:4d} {w:8.0f} {d:7.1f}\n")
print(f"strait faces written to {FACES_FILE}")
print(f"ocean cells: {wet.sum()}, depth {depth[wet].min():.1f}-{depth[wet].max():.0f} m")

# ============================================================== 9. write
elev_out = (-depth).astype(np.float32)
mask = wet.astype(np.uint8)

with Dataset(OFILE, "w", format="NETCDF4") as dst:
    for k, v in gatts.items():
        dst.setncattr(k, v)
    dst.history = f"{gatts.get('history', '')}\n{' '.join(sys.argv)}"
    ny, nx = depth.shape
    dst.createDimension("y", ny)
    dst.createDimension("x", nx)

    def var(name, data, dtype, **att):
        v = dst.createVariable(name, dtype, ("y", "x"), zlib=True)
        v.setncatts(att)
        v[:] = data

    var("lon", lon, "f4", standard_name="longitude", units="degrees_east")
    var("lat", lat, "f4", standard_name="latitude", units="degrees_north")
    var("elevation", elev_out, "f4", long_name="Elevation relative to sea level",
        units="m", coordinates="lat lon")
    var("mask", mask, "u1", standard_name="sea_binary_mask", units="1",
        coordinates="lat lon")
    var("edited", edited, "u1", coordinates="lat lon",
        long_name="hand edit: 0 none, 1 island/closure, 2 strait, 3 minimum depth")

with Dataset("mask.nc", "w", format="NETCDF4") as m:
    m.createDimension("y", depth.shape[0])
    m.createDimension("x", depth.shape[1])
    for name, data, dt in (("lon", lon, "f4"), ("lat", lat, "f4"), ("mask", mask, "u1")):
        v = m.createVariable(name, dt, ("y", "x"))
        v[:] = data
    m["lon"].setncatts({"standard_name": "longitude", "long_name": "longitude",
                        "units": "degrees_east"})
    m["lat"].setncatts({"standard_name": "latitude", "long_name": "latitude",
                        "units": "degrees_north"})
    m["mask"].standard_name = "sea_binary_mask"
    m["mask"].units = "1"
    m["mask"].coordinates = "lat lon"

os.makedirs(INPUT_DIR, exist_ok=True)
binfile = os.path.join(INPUT_DIR, os.path.splitext(os.path.basename(OFILE))[0] + ".bin")
elev_out.astype(">f4").tofile(binfile)
print(f"wrote {OFILE}, mask.nc, {binfile}")

if os.path.exists(RBCS_NC):
    with Dataset(RBCS_NC, "r+") as ds:
        mr = np.asarray(ds["maskrbcs"][:])
        mr = np.where(mask[None, :, :] > 0, mr, 0.0)
        ds["maskrbcs"][:] = mr
    mr.astype(">f4").tofile(os.path.join(INPUT_DIR, "maskrbcs.bin"))
    print("updated maskrbcs.nc and maskrbcs.bin")
else:
    print(f"{RBCS_NC} not found: RBCS mask not updated")
