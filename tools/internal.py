#!/usr/bin/env python3

import os
import sys
import f90nml
import numpy as np
from netCDF4 import Dataset

namelist_file = sys.argv[1]
namelist = f90nml.read(namelist_file)

nspgx = namelist["boundaryparam"]["nspgx"]

domain = namelist["terrainparam"]["domname"]
inpdir = namelist["terrainparam"]["dirter"]

ncfile = Dataset(os.path.join(inpdir,domain+'_DOMAIN000.nc'),'r')
lats = ncfile.variables['xlat'][:]
lons = ncfile.variables['xlon'][:]

lons = np.where(lons<0,lons+360,lons)
ny,nx = np.shape(lats)

print('TLC : ', f"{lons[ny-nspgx,nspgx]:7.3f}, {lats[ny-nspgx,nspgx]:7.3f}")
print('CNB : ', f"{lons[ny-nspgx,nx//2]:7.3f}, {lats[ny-nspgx,nx//2]:7.3f}")
print('TRC : ', f"{lons[ny-nspgx,nx-nspgx]:7.3f}, {lats[ny-nspgx,nx-nspgx]:7.3f}")
print('CWB : ', f"{lons[ny//2,nspgx]:7.3f}, {lats[ny//2,nspgx]:7.3f}")
print('CPD : ', f"{lons[ny//2,nx//2]:7.3f}, {lats[ny//2,nx//2]:7.3f}")
print('CEB : ', f"{lons[ny//2,nx-nspgx]:7.3f}, {lats[ny//2,nx-nspgx]:7.3f}")
print('BLC : ', f"{lons[nspgx,nspgx]:7.3f}, {lats[nspgx,nspgx]:7.3f}")
print('CSB : ', f"{lons[nspgx,nx//2]:7.3f}, {lats[nspgx,nx//2]:7.3f}")
print('BRC : ', f"{lons[nspgx,nx-nspgx]:7.3f}, {lats[nspgx,nx-nspgx]:7.3f}")

ncfile.close( )
