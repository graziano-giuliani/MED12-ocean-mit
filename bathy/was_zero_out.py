#!/usr/bin/env python3

import os
import sys
import numpy as np
from netCDF4 import Dataset
import regionmask
from cdo import *

# Fine correction of bathinetric data

land_110 = regionmask.defined_regions.natural_earth_v5_0_0.land_110

def newname(name):
    if name == 'z':
        return 'elevation'
    else:
        return name

try:
    ifile = sys.argv[1]
    ofile = sys.argv[2]
except:
    ifile = "MIT_BATHY.nc"
    ofile = "BATHYMETRY.nc"

with Dataset(ifile,"r") as src, Dataset(ofile, "w") as dst:
    lon = src.variables['lon'][:]
    lat = src.variables['lat'][:]
    # copy global attributes all at once via dictionary
    dst.setncatts(src.__dict__)
    # copy dimensions
    for name, dimension in src.dimensions.items():
        dst.createDimension(
            name, (len(dimension) if not dimension.isunlimited() else None))
    # copy all file data except for the excluded
    for name, variable in src.variables.items():
        x = dst.createVariable(newname(name), variable.datatype, variable.dimensions)
        if name not in ["elevation", "z"]:
            dst[name][:] = src[name][:]
        # copy variable attributes all at once via dictionary
        dst[newname(name)].setncatts(src[name].__dict__)
    try:
        bathy = src.variables['elevation'][:]
    except:
        bathy = -src.variables['z'][:]

    # Remove greater than zero values
    bathy = np.where(bathy > -1.0, 0.0, bathy)
    land = np.isnan(land_110.mask(lon,lat))
    bathy[np.where(~land)] = 0.0

    # Remove not connected pixels
    nj,ni = np.shape(bathy)
    for i in range(1,ni-1):
       for j in range(1,nj-1):
           if bathy[j,i] < 0.0:
               if all(np.array((bathy[j-1,i],bathy[j+1,i],
                                bathy[j,i+1],bathy[j,i-1])) > -0.5):
                   bathy[j,i] = 0.0

    # FINE TUNE FOR WAS
    # Med and red sea antennas
    bathy[397:,0:64] = 0.0

    # Shattel arab lake?
    bathy[416:418,146:148] = 0.0

    bathy[319,219:222] = 0.0
    bathy[361:363,325] = 0.0
    bathy[348,533] = 0.0
    bathy[350,533] = 0.0
    bathy[348,535] = 0.0
    bathy[349,533] = 0.0
    bathy[349,536] = 0.0
    bathy[347,535] = 0.0
    bathy[350,536] = 0.0
    bathy[352,536:541] = 0.0
    bathy[324,560] = 0.0
    bathy[106,216] = -25.0
    bathy[61,32] = -25.0

    mask1 = (bathy < 0.0)
    mask2 = (bathy > -25.0)
    mask = (mask1 & mask2)
    bathy = np.where(mask,-25.0,bathy)
    bathy = np.where(bathy<-5800,-5800,bathy)

    dst.variables['elevation'][:] = bathy

    try:
        smask = dst.createVariable("mask","u1",("lon","lat"))
    except:
        smask = dst.createVariable("mask","u1",("y","x"))
    smask.standard_name = "sea_binary_mask"
    smask.units = "1"
    smask.coordinates = "lat lon"
    dst.variables['mask'][:] = np.where(bathy > -1,0,1) 

    binfile = os.path.join('../input',os.path.splitext(ofile)[0]+".bin")
    with open(binfile,"w") as fbin:
        bathy.astype('>f4').tofile(fbin)

cdo = cdo.Cdo( )
cdo.selvar("mask",input=ofile, output="mask.nc")
