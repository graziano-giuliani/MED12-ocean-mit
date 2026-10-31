#!/usr/bin/env python3
"""
Cell-average a high-resolution bathymetry (e.g. EMODnet DTM, ~115 m) onto a
curvilinear MITgcm grid.

Replaces `cdo remapdis,grid,128`, which only averages a ~1 km patch around each
cell centre (effectively point sampling a ~7 km cell).

Method
------
Every source pixel is assigned to the model cell whose centre (XC, YC) is
nearest on the sphere (KD-tree in 3-D Cartesian coordinates). For a smooth,
near-orthogonal grid these Voronoi cells coincide closely with the real C-grid
tracer cells. Pixels farther from their nearest centre than that cell's
spacing are outside the domain and are dropped. The source is read in
latitude bands, so the 900 MB file never has to fit in memory.

For every model cell the output contains:
  elevation       negative depth, mean over the WET pixels of the cell,
                  0 where wet_fraction < --wet-threshold (land)
  wet_fraction    fraction of source pixels that are ocean (0..1)
  depth_mean_wet  mean depth of wet pixels, no land/sea decision applied
  depth_max       deepest pixel in the cell (thalweg: useful for straits)
  depth_volume    cell-mean depth counting land as 0 m (volume-preserving)
  n_pixels        number of source pixels that fell in the cell

No 'mask' variable is written, so the file can go straight into zero_out.py.
Land in the source may be NaN/fill (EMODnet DTM) or positive elevation
(merged products); both are treated as land.

Usage
-----
  python remap_bathymetry.py SOURCE.nc TARGET_GRID.nc OUT.nc \
         [--wet-threshold 0.5] [--stride 1] [--band 64]

TARGET_GRID.nc must contain 2-D lon(y,x) and lat(y,x) of the tracer points.
These must be exactly the XC/YC MITgcm uses (check against the model's grid
output); the BATHYMETRY.nc you have now can serve as the grid file.
"""

import argparse
import sys
import time

import numpy as np
from netCDF4 import Dataset
from scipy.spatial import cKDTree

R_EARTH = 6371.0e3


def to_xyz(lon, lat):
    lo = np.radians(lon)
    la = np.radians(lat)
    c = np.cos(la)
    return np.stack((c * np.cos(lo), c * np.sin(lo), np.sin(la)), axis=-1)


def find_var(ds, candidates, what):
    for name in candidates:
        if name in ds.variables:
            return name
    sys.exit(f"Cannot find {what} variable (tried {candidates}) in {ds.filepath()}")


def local_spacing(xyz):
    """Largest chord distance from each centre to its 4 neighbours."""
    ny, nx, _ = xyz.shape
    d = np.zeros((ny, nx))
    for axis in (0, 1):
        diff = np.linalg.norm(np.diff(xyz, axis=axis), axis=-1)
        pad_lo = [(0, 0), (0, 0)]
        pad_hi = [(0, 0), (0, 0)]
        pad_lo[axis] = (1, 0)
        pad_hi[axis] = (0, 1)
        d = np.maximum(d, np.pad(diff, pad_lo, mode="edge"))
        d = np.maximum(d, np.pad(diff, pad_hi, mode="edge"))
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="high-resolution bathymetry (regular lon/lat)")
    p.add_argument("grid", help="netCDF with 2-D lon(y,x), lat(y,x) of model tracer points")
    p.add_argument("output", help="output netCDF")
    p.add_argument("--wet-threshold", type=float, default=0.5,
                   help="minimum wet fraction for a cell to be ocean (default 0.5)")
    p.add_argument("--stride", type=int, default=1,
                   help="use every N-th source pixel in each direction (default 1)")
    p.add_argument("--band", type=int, default=64,
                   help="source rows per chunk (default 64)")
    a = p.parse_args()

    # ---------------------------------------------------------------- target
    with Dataset(a.grid) as g:
        glon = np.asarray(g[find_var(g, ["lon", "XC", "nav_lon"], "lon")][:], dtype=np.float64)
        glat = np.asarray(g[find_var(g, ["lat", "YC", "nav_lat"], "lat")][:], dtype=np.float64)
    if glon.ndim != 2:
        sys.exit("Target lon/lat must be 2-D (y, x).")
    ny, nx = glon.shape
    gxyz = to_xyz(glon, glat)
    tree = cKDTree(gxyz.reshape(-1, 3))
    # A pixel inside cell (j,i) is at most ~half a diagonal from its centre;
    # allow the full neighbour spacing as the rejection radius.
    radius = local_spacing(gxyz).ravel()

    lon_min, lon_max = glon.min() - 0.5, glon.max() + 0.5
    lat_min, lat_max = glat.min() - 0.5, glat.max() + 0.5

    ncell = ny * nx
    n_all = np.zeros(ncell, dtype=np.int64)
    n_wet = np.zeros(ncell, dtype=np.int64)
    sum_wet = np.zeros(ncell, dtype=np.float64)
    max_dep = np.zeros(ncell, dtype=np.float64)

    # ---------------------------------------------------------------- source
    with Dataset(a.source) as s:
        vlon = find_var(s, ["lon", "longitude", "x"], "lon")
        vlat = find_var(s, ["lat", "latitude", "y"], "lat")
        vz = find_var(s, ["elevation", "z", "depth", "Band1"], "elevation")
        slon = np.asarray(s[vlon][:], dtype=np.float64)
        slat = np.asarray(s[vlat][:], dtype=np.float64)
        if slon.ndim != 1 or slat.ndim != 1:
            sys.exit("Source must be on a regular grid with 1-D lon and lat.")
        zvar = s[vz]
        zvar.set_auto_mask(True)
        dims = zvar.dimensions
        lat_first = dims.index(s[vlat].dimensions[0]) == 0

        ilon = np.where((slon >= lon_min) & (slon <= lon_max))[0]
        ilat = np.where((slat >= lat_min) & (slat <= lat_max))[0]
        i0, i1 = ilon[0], ilon[-1] + 1
        rows = ilat[::a.stride]
        sub_lon = slon[i0:i1:a.stride]
        print(f"Source pixels used: {len(rows)} x {len(sub_lon)} "
              f"= {len(rows) * len(sub_lon) / 1e6:.0f} M", flush=True)

        t0 = time.time()
        for b in range(0, len(rows), a.band):
            r = rows[b:b + a.band]
            j0, j1 = r[0], r[-1] + 1
            if lat_first:
                blk = zvar[j0:j1:a.stride, i0:i1:a.stride]
            else:
                blk = zvar[i0:i1:a.stride, j0:j1:a.stride].T
            blk = np.ma.filled(blk.astype(np.float64), np.nan)

            LON, LAT = np.meshgrid(sub_lon, slat[j0:j1:a.stride])
            dist, idx = tree.query(to_xyz(LON.ravel(), LAT.ravel()), workers=-1)
            z = blk.ravel()
            inside = dist <= radius[idx]
            idx, z = idx[inside], z[inside]

            wet = np.isfinite(z) & (z < 0.0)
            n_all += np.bincount(idx, minlength=ncell)
            n_wet += np.bincount(idx[wet], minlength=ncell)
            sum_wet += np.bincount(idx[wet], weights=-z[wet], minlength=ncell)

            if wet.any():
                iw, dw = idx[wet], -z[wet]
                order = np.argsort(iw, kind="stable")
                iw, dw = iw[order], dw[order]
                starts = np.flatnonzero(np.r_[True, iw[1:] != iw[:-1]])
                cells = iw[starts]
                max_dep[cells] = np.maximum(max_dep[cells],
                                            np.maximum.reduceat(dw, starts))

            done = min(b + a.band, len(rows)) / len(rows)
            el = time.time() - t0
            print(f"\r  {100 * done:5.1f} %  ({el / 60:.1f} min, "
                  f"~{el / done / 60 - el / 60:.1f} min left)", end="", flush=True)
        print()

    # ---------------------------------------------------------------- fields
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(n_all > 0, n_wet / n_all, 0.0)
        mean_wet = np.where(n_wet > 0, sum_wet / n_wet, 0.0)
    volume = mean_wet * frac
    ocean = frac >= a.wet_threshold
    elev = np.where(ocean, -mean_wet, 0.0)

    empty = (n_all == 0).sum()
    if empty:
        print(f"WARNING: {empty} model cells received no source pixels "
              f"(source does not cover them, or stride too large); set to land.")
    print(f"Ocean cells: {ocean.sum()} of {ncell}; "
          f"shallowest ocean depth {mean_wet[ocean].min():.1f} m; "
          f"deepest {mean_wet[ocean].max():.0f} m")

    def shp(x):
        return x.reshape(ny, nx)

    # ---------------------------------------------------------------- write
    with Dataset(a.output, "w", format="NETCDF4") as o:
        o.createDimension("y", ny)
        o.createDimension("x", nx)
        o.title = "Cell-averaged bathymetry for MITgcm"
        o.source = a.source
        o.method = ("nearest-centre (Voronoi) cell averaging of source pixels; "
                    f"wet_threshold={a.wet_threshold}, stride={a.stride}")
        o.history = " ".join(sys.argv)

        def var(name, data, dtype="f4", **att):
            v = o.createVariable(name, dtype, ("y", "x"), zlib=True)
            v.setncatts(att)
            v[:] = data

        var("lon", glon, standard_name="longitude", units="degrees_east")
        var("lat", glat, standard_name="latitude", units="degrees_north")
        var("elevation", shp(elev), long_name="Elevation relative to sea level "
            "(negative = depth), mean over wet pixels, 0 = land",
            units="m", coordinates="lat lon")
        var("wet_fraction", shp(frac), long_name="Fraction of ocean source pixels",
            units="1", coordinates="lat lon")
        var("depth_mean_wet", shp(mean_wet), long_name="Mean depth of wet pixels",
            units="m", coordinates="lat lon")
        var("depth_max", shp(max_dep), long_name="Deepest source pixel in cell",
            units="m", coordinates="lat lon")
        var("depth_volume", shp(volume), long_name="Cell-mean depth with land as 0",
            units="m", coordinates="lat lon")
        var("n_pixels", shp(n_all), dtype="i4", long_name="Source pixels in cell",
            coordinates="lat lon")
    print(f"Wrote {a.output}")


if __name__ == "__main__":
    main()
