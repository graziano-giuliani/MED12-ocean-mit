#!/usr/bin/env python3
"""
Narrow the hand-routed straits by reducing the face lengths in DXG/DYG.

On the MITgcm C-grid the volume/tracer transport through a face is
    U face (i,j):  uVel * dyG(i,j) * drF * hFacW      (zonal flow)
    V face (i,j):  vVel * dxG(i,j) * drF * hFacS      (meridional flow)
so the width of a channel is set ONLY by DYG at U faces and DXG at V faces.
Continuity and tracer budgets use the same transports, so the model stays
conservative.

Deliberately NOT changed:
  DXC, DYC  distances between cell centres = channel LENGTH, not width;
            changing them alters pressure gradients and travel distances.
  DXF, DYF, DXV, DYU  enter the viscous/vorticity operators and the grid
            length scales of the Leith/biharmonic viscosity and its stability
            limits; shrinking them 5-10x would cut the stable biharmonic
            viscosity by up to 10^4 and can make the run blow up.
  RA, RAW, RAS, RAZ  cell areas: keeping them keeps the strait cells' volume
            (a small extra reservoir), harmless for conservation.

A face is narrowed only if
  (a) it is a BRIDGE of the ocean grid: removing it would disconnect the
      basins, i.e. it belongs to the one-cell channel (flow cannot go around), and
  (b) at least one of its two cells was land in the cell-averaged
      interpolation (wet_fraction < --land-fraction): the channel there is
      genuinely narrower than a grid cell. Cells that are mostly water, such
      as the mouths or the entrance of the Gulf of Corinth, keep their width.

Usage
  python narrow_straits.py --interp MIT_BATHY.nc [--faces strait_faces.txt]
                           [--bathy BATHYMETRY.nc] [--grid-dir .]
                           [--out-dir narrowed] [--prec 32] [--land-fraction 0.5]
"""

import argparse
import os
import shutil

import numpy as np
from netCDF4 import Dataset
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import breadth_first_order

# ------------------------------------------------------------------ widths
# Target widths in metres. CHECK THESE AGAINST A CHART: they are typical
# literature values, not measured for your exact face positions.
# WIDTH: default for every bridge face of a strait (None = leave untouched).
# FACE_WIDTH: overrides for single faces, keyed (strait, type, j, i) with the
# 1-based indices exactly as written in strait_faces.txt.
WIDTH = {
    "Bosphorus":      1500.0,   # 0.7-3.7 km, mean ~1.5 km
    "Dardanelles":    4000.0,   # 1.2-6 km
    "Rion-Antirrion": 2000.0,   # ~2 km at the bridge
    "Oreoi":          None,     # several km: left at grid width
}
FACE_WIDTH = {
    ("Bosphorus",   "V", 190, 475): 700.0,    # Rumelihisari narrows, ~41.09N
    ("Dardanelles", "V", 169, 444): 1300.0,   # Canakkale narrows, ~40.15N
}


def read_faces(path):
    faces = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            name, t, j, i, w, d = line.split()
            faces.append((name, t, int(j), int(i), float(w), float(d)))
    return faces


def ocean_graph(wet):
    ny, nx = wet.shape
    idx = -np.ones(wet.shape, dtype=np.int64)
    idx[wet] = np.arange(wet.sum())
    rows, cols = [], []
    for a, b in ((idx[:, :-1], idx[:, 1:]), (idx[:-1, :], idx[1:, :])):
        ok = (a >= 0) & (b >= 0)
        rows += [a[ok], b[ok]]
        cols += [b[ok], a[ok]]
    r = np.concatenate(rows)
    c = np.concatenate(cols)
    g = coo_matrix((np.ones(len(r), dtype=np.int8), (r, c)),
                   shape=(wet.sum(), wet.sum())).tocsr()
    return g, idx


def is_bridge(g, n1, n2):
    h = g.copy().tolil()
    h[n1, n2] = 0
    h[n2, n1] = 0
    h = h.tocsr()
    h.eliminate_zeros()
    reached = breadth_first_order(h, n1, directed=False, return_predecessors=False)
    return n2 not in set(reached.tolist())


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--faces", default="strait_faces.txt")
    p.add_argument("--bathy", default="BATHYMETRY.nc", help="output of zero_out.py (needs 'mask')")
    p.add_argument("--interp", required=True,
                   help="output of remap_bathymetry.py (needs 'wet_fraction')")
    p.add_argument("--land-fraction", type=float, default=0.5,
                   help="a cell with wet_fraction below this was land before routing")
    p.add_argument("--grid-dir", default=".", help="directory with DXG.bin, DYG.bin")
    p.add_argument("--out-dir", default="narrowed", help="where modified files are written")
    p.add_argument("--prec", type=int, default=32, choices=(32, 64))
    a = p.parse_args()

    with Dataset(a.bathy) as d:
        wet = np.asarray(d["mask"][:]) > 0
    with Dataset(a.interp) as d:
        wf = np.asarray(d["wet_fraction"][:])
    ny, nx = wet.shape
    dt = ">f4" if a.prec == 32 else ">f8"

    grid = {}
    for name in ("DXG", "DYG"):
        f = os.path.join(a.grid_dir, name + ".bin")
        arr = np.fromfile(f, dt)
        if arr.size != ny * nx:
            raise SystemExit(f"{f}: {arr.size} values, expected {ny}x{nx}; check --prec")
        grid[name] = arr.reshape(ny, nx)
    orig = {k: v.copy() for k, v in grid.items()}

    g, idx = ocean_graph(wet)
    print(f"{'strait':16s} face   j    i   cells        width now -> new   note")
    for name, t, j, i, w_est, depth in read_faces(a.faces):
        j0, i0 = j - 1, i - 1                          # 0-based
        if t == "U":
            c1, c2, var = (j0, i0 - 1), (j0, i0), "DYG"
        else:
            c1, c2, var = (j0 - 1, i0), (j0, i0), "DXG"
        now = grid[var][j0, i0]
        tag = f"{name:16s} {t}  {j:4d} {i:4d}  {var}"
        if not (wet[c1] and wet[c2]):
            print(f"{tag} {now:8.0f}             SKIP: face not between two wet cells")
            continue
        target = FACE_WIDTH.get((name, t, j, i), WIDTH.get(name))
        if target is None:
            print(f"{tag} {now:8.0f}             no target width set")
            continue
        if min(wf[c1], wf[c2]) >= a.land_fraction:
            print(f"{tag} {now:8.0f}             mostly water (wf {wf[c1]:.2f}/{wf[c2]:.2f}): unchanged")
            continue
        if not is_bridge(g, idx[c1], idx[c2]):
            print(f"{tag} {now:8.0f}             open water (not a bridge): unchanged")
            continue
        if target >= now:
            print(f"{tag} {now:8.0f}             target {target:.0f} >= grid width: unchanged")
            continue
        grid[var][j0, i0] = target
        print(f"{tag} {now:8.0f} -> {target:6.0f}   factor {target / now:.2f}")

    os.makedirs(a.out_dir, exist_ok=True)
    for name, arr in grid.items():
        changed = int((arr != orig[name]).sum())
        out = os.path.join(a.out_dir, name + ".bin")
        arr.astype(dt).tofile(out)
        print(f"wrote {out} ({changed} faces changed)")


if __name__ == "__main__":
    main()
