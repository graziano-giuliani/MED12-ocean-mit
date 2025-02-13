#!/usr/bin/env python3

import sys
import numpy as np
from netCDF4 import Dataset

# Fine correction of bathinetric data

ifile = sys.argv[1]
ofile = sys.argv[2]

with Dataset(ifile,"r") as src, Dataset(ofile, "w") as dst:
    # copy global attributes all at once via dictionary
    dst.setncatts(src.__dict__)
    # copy dimensions
    for name, dimension in src.dimensions.items():
        dst.createDimension(
            name, (len(dimension) if not dimension.isunlimited() else None))
    # copy all file data except for the excluded
    for name, variable in src.variables.items():
        x = dst.createVariable(name, variable.datatype, variable.dimensions)
        if name not in ["elevation"]:
            dst[name][:] = src[name][:]
        # copy variable attributes all at once via dictionary
        dst[name].setncatts(src[name].__dict__)
    bathy = src.variables['elevation'][:]

    bathy[0:25,0:62] = 0.0
    bathy[130:,0:62] = 0.0
    bathy[125,20] = 0.0
    bathy[103,46] = 0.0
    bathy[103,47] = 0.0
    bathy[261,282] = 0.0
    bathy[251,296] = 0.0
    bathy[233,308] = 0.0
    bathy[233,309] = 0.0
    bathy[212,333] = 0.0
    bathy[130:199:,0:110] = 0.0
    bathy[200:,0:120] = 0.0
    bathy[201,248] = 0.0
    bathy[200,249] = 0.0
    bathy[81,280] = 0.0
    bathy[53,259] = 0.0
    bathy[141,381] = 0.0
    bathy[141,380] = 0.0
    bathy[142,380] = 0.0
    bathy[176,447] = 0.0
    bathy[174,447] = 0.0
    bathy[214,453] = 0.0
    bathy[230,456] = 0.0
    bathy[291,516] = 0.0
    bathy[303,531] = 0.0
    bathy[289,515] = 0.0
    bathy[300:,0:180] = 0.0
    bathy[0:10,500:] = 0.0
    bathy[188,473] = bathy[187,473]
    bathy[188,474] = bathy[187,473]
    bathy[191,474] = bathy[191,475]
    bathy[169,442] = bathy[169,441]
    bathy[170,445] = bathy[170,444]
    bathy[171,446] = bathy[171,445]
    bathy[172,447] = bathy[172,446]
    bathy[318,492] = 0.0
    bathy[318,492] = 0.0
    bathy[166,406] = 0.0
    bathy[169,413] = 0.0
    bathy[143,380] = 0.0
    bathy[107,246] = 0.0
    bathy[107,247] = 0.0
    bathy[112,467] = 0.0
    bathy[112,468] = 0.0
    bathy[170,413] = 0.0
    bathy[318,573] = 0.0
    bathy[118,457] = 0.0
    bathy[109,469] = 0.0
    bathy[148,441] = 0.0
    bathy[149,441] = 0.0
    bathy[149,442] = 0.0
    bathy[142,402] = 0.0
    bathy[198,247] = 0.0
    bathy[194,254] = 0.0
    bathy[193,258] = 0.0
    bathy[171,280] = 0.0
    bathy[169,287] = 0.0
    bathy[163,430] = 0.0
    bathy[317:,495:500] = 0.0
    bathy[352:359,572:579] = 0.0

    for nt in range(0,3):
        for i in range(1,660):
            for j in range(1,368):
                if bathy[j,i] == 1:
                    if all((bathy[j-1,i],bath[j+1,i],
                            bathy[j,i+1],bathy[j,i-1]) == 0):
                        bathy[j,i] = 0.0

    bathy[142,404] = bathy[143,404]
    bathy[142,403] = bathy[143,403]

    mask1 = (bathy < 0.0)
    mask2 = (bathy > -10.0)
    mask = (mask1 & mask2)
    bathy = np.where(mask,-10.0,bathy)

    dst.variables['elevation'][:] = bathy

    smask = dst.createVariable("mask","u1",("lon","lat"))
    smask.standard_name = "sea_binary_mask"
    smask.units = "1"
    smask.coordinates = "lat lon"
    dst.variables['mask'][:] = np.where(bathy > -1,0,1) 
