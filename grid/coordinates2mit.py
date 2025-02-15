#!/usr/bin/env python3

import os
import sys
import yaml
import numpy as np
import xarray as xr
from netCDF4 import Dataset
from cdo import *

with open("rbcsbdy.yaml","r") as f:
    configbdy = yaml.safe_load(f)

try:
    ds = Dataset(sys.argv[1],'r')
except:
    ds = Dataset('1_coordinates_ORCA_R12.nc','r')

LONC = ds.variables['nav_lon'][1:-1,1:-1].data
LATC = ds.variables['nav_lat'][1:-1,1:-1].data

LONG = ds.variables['glamu'][0,1:-1,0:-2].data
LATG = ds.variables['gphiv'][0,0:-2,1:-1].data

DXF  = ds.variables['e1t'][0,1:-1,1:-1].data
DYF  = ds.variables['e2t'][0,1:-1,1:-1].data

DXG  = ds.variables['e1v'][0,0:-2,1:-1].data
DYG  = ds.variables['e2u'][0,1:-1,0:-2].data

DXC  = ds.variables['e1u'][0,1:-1,0:-2].data
DYC  = ds.variables['e2v'][0,0:-2,1:-1].data

DXV  = ds.variables['e1f'][0,0:-2,0:-2].data
DYU  = ds.variables['e2f'][0,0:-2,0:-2].data

RA   = DXF*DYF
RAW  = DXC*DYG
RAS  = DXG*DYC
RAZ  = DXV*DYU

with open("../input/LONC.bin","wb") as fo:
    LONC.astype('>f4').tofile(fo)
with open("../input/LATC.bin","wb") as fo:
    LATC.astype('>f4').tofile(fo)
with open("../input/LONG.bin","wb") as fo:
    LONG.astype('>f4').tofile(fo)
with open("../input/LATG.bin","wb") as fo:
    LATG.astype('>f4').tofile(fo)
with open("../input/DXF.bin","wb") as fo:
    DXF.astype('>f4').tofile(fo)
with open("../input/DYF.bin","wb") as fo:
    DYF.astype('>f4').tofile(fo)
with open("../input/DXG.bin","wb") as fo:
    DXG.astype('>f4').tofile(fo)
with open("../input/DYG.bin","wb") as fo:
    DYG.astype('>f4').tofile(fo)
with open("../input/DXC.bin","wb") as fo:
    DXC.astype('>f4').tofile(fo)
with open("../input/DYC.bin","wb") as fo:
    DYC.astype('>f4').tofile(fo)
with open("../input/DXV.bin","wb") as fo:
    DXV.astype('>f4').tofile(fo)
with open("../input/DYU.bin","wb") as fo:
    DYU.astype('>f4').tofile(fo)
with open("../input/RA.bin","wb") as fo:
    RA.astype('>f4').tofile(fo)
with open("../input/RAW.bin","wb") as fo:
    RAW.astype('>f4').tofile(fo)
with open("../input/RAS.bin","wb") as fo:
    RAS.astype('>f4').tofile(fo)
with open("../input/RAZ.bin","wb") as fo:
    RAZ.astype('>f4').tofile(fo)

ds = Dataset("depth.nc",'r')
depth = ds.variables["depth"]

nx, ny = np.shape(LATC)
nz = depth.size

maskbdy = np.zeros((nz,nx,ny))
npnts = configbdy["npoints"]
frac = 1.0/float(npnts)
if configbdy["rbcs"]["north"]:
    for k in range(nz):
        for j in range(ny):
            maskbdy[k,-npnts:,j] = np.linspace(frac,1.0,npnts)
if configbdy["rbcs"]["south"]:
    for k in range(nz):
        for j in range(ny):
            maskbdy[k,0:npnts,j] = np.linspace(1.0,frac,npnts)
if configbdy["rbcs"]["east"]:
    for k in range(nz):
        for i in range(nx):
            maskbdy[k,i,-npnts:] = np.linspace(frac,1.0,npnts)
if configbdy["rbcs"]["west"]:
    for k in range(nz):
        for i in range(nx):
            maskbdy[k,i,0:npnts] = np.linspace(1.0,frac,npnts)

xlon = xr.DataArray(name = "lon",
                    data = LONC,
                    dims = ["lon","lat"],
                    attrs = dict(standard_name = "longitude",
                                 units = "degrees_east"))
xlat = xr.DataArray(name = "lat",
                    data = LATC,
                    dims = ["lon","lat"],
                    attrs = dict(standard_name = "latitude",
                                 units = "degrees_north"))
xdepth = xr.DataArray(name = "depth",
                      data = depth,
                      dims = ["depth"],
                      attrs = dict(standard_name = "depth",
                                   units = "m"))

da = xr.DataArray(name = "maskrbcs" , data=maskbdy,
                  dims = ["depth","lon","lat"],
                  coords = dict(lon = xlon,
                                lat = xlat,
                                depth = xdepth),
                  attrs = dict(standard_name = "maskrbcs",
                               units = "1",
                               coordinates = "depth lat lon"),
                 )
da.to_netcdf('maskrbcs.nc')

with open("../input/maskrbcs.bin","wb") as fo:
    maskbdy.astype('>f4').tofile(fo)

cdo = cdo.Cdo( )
grid_description = cdo.griddes(input="maskrbcs.nc")
with open("../bathy/grid_description.des","w") as f:
    for line in grid_description:
        f.write(line+os.linesep)
