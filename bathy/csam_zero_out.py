#!/usr/bin/env python3

import os
import sys
import numpy as np
from netCDF4 import Dataset
import regionmask
from cdo import *

# Fine correction of bathinetric data

land_50 = regionmask.defined_regions.natural_earth_v5_1_2.land_50

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
    bathy = np.where(bathy >= 0.0, 0.0, bathy)
    land = np.isnan(land_50.mask(lon,lat))
    bathy[np.where(~land)] = 0.0

    # Remove not connected pixels
    nj,ni = np.shape(bathy)
    for i in range(1,ni-1):
       for j in range(1,nj-1):
           if bathy[j,i] < 0.0:
               if all(np.array((bathy[j-1,i],bathy[j+1,i],
                                bathy[j,i+1],bathy[j,i-1])) > -0.5):
                   bathy[j,i] = 0.0

    # FINE TUNE FOR CSAM
    # South
    bathy[:,0:42] = 0.0
    bathy[1006:1016,1054:1065] = 0.0
    bathy[1012,1068] = 0.0
    bathy[1005,1066] = 0.0
    bathy[1007,1065] = 0.0
    bathy[1010,1066] = 0.0
    bathy[976,1050] = 0.0
    bathy[747,784:786] = 0.0
    bathy[742,805] = 0.0
    bathy[747,707:711] = 0.0
    bathy[745,708] = 0.0
    bathy[749,779] = bathy[749,780]
    bathy[746,709] = 0.0
    bathy[745,709] = 0.0
    bathy[746,701] = 0.0
    bathy[778,758] = 0.0
    bathy[736,659] = 0.0
    bathy[719,669] = 0.0
    bathy[720,676] = 0.0
    bathy[720,630] = bathy[721,630]
    bathy[709,644] = bathy[710,644]
    bathy[657,554] = bathy[656,553]
    bathy[485,254] = bathy[485,255]
    bathy[493,270] = 0.0
    bathy[412,224] = bathy[412,225]
    bathy[641,466] = 0.0
    bathy[726,680] = 0.0
    bathy[288,243] = 0.0
    bathy[735,678] = 0.0
    bathy[735,679] = 0.0
    bathy[736,658] = 0.0
    bathy[719,628] = 0.0
    bathy[716,635] = 0.0
    bathy[745,700] = 0.0
    bathy[748,779] = bathy[748,780]
    bathy[735,678:670] = 0.0
    bathy[750,782] = 0.0
    bathy[738,727] = 0.0
    bathy[744,708] = 0.0
    bathy[737,671] = 0.0
    bathy[629,526] = bathy[630,526]
    bathy[487,248] = bathy[488,248]
    bathy[637,467] = 0.0
    bathy[733,631] = 0.0
    bathy[716,634] = 0.0
    bathy[715,635] = 0.0
    bathy[687,582] = 0.0
    bathy[680,567] = 0.0
    bathy[661,530] = 0.0
    bathy[662,521] = 0.0
    bathy[642,465] = 0.0
    bathy[642,466] = 0.0
    bathy[642,467] = 0.0
    bathy[643,465] = 0.0
    bathy[595,387] = 0.0
    bathy[533,300] = 0.0
    bathy[533,301] = 0.0
    bathy[533,302] = 0.0
    bathy[534,301] = 0.0
    bathy[534,302] = 0.0
    bathy[488,240] = 0.0
    bathy[503,253] = 0.0
    bathy[485,252] = -10.0
    bathy[485,255] = -10.0
    bathy[420,237] = -10.0
    bathy[502:510,267:276] = 0.0
    bathy[505:514,250:266] = 0.0
    bathy[485:501,222:232] = 0.0
    bathy[448:458,225:235] = 0.0
    bathy[363,230] = 0.0
    bathy[408,223] = 0.0
    bathy[333,236] = 0.0
    bathy[363,230] = 0.0
    bathy[302,240] = 0.0
    bathy[321,242] = 0.0
    bathy[319,246] = 0.0
    bathy[243,288] = 0.0
    bathy[217,230] = 0.0
    bathy[286,241] = 0.0
    bathy[269,239] = 0.0
    bathy[260,238] = 0.0
    bathy[260,243] = 0.0
    bathy[280,238] = bathy[281,238]
    bathy[280,239] = bathy[281,239]
    bathy[280,240] = bathy[281,240]
    bathy[189,216:220] = 0.0
    bathy[188,217:219] = 0.0
    bathy[179,211] = 0.0
    bathy[179,211] = 0.0
    bathy[758,778] = 0.0
    bathy[741,704] = bathy[742,704]
    bathy[738,702] = 0.0
    bathy[661,526] = bathy[661,527]
    bathy[640,463] = 0.0
    bathy[646,478] = 0.0
    bathy[491,266] = bathy[491,267]
    bathy[502,263] = 0.0
    bathy[501,253] = 0.0
    bathy[483,253] = 0.0
    bathy[451,239] = 0.0
    bathy[409,223] = 0.0
    bathy[285,242] = 0.0
    bathy[640,464] = 0.0
    bathy[738,701] = 0.0
    bathy[634,718] = 0.0
    bathy[641,463] = 0.0
    bathy[504,252] = 0.0
    bathy[504,253] = 0.0
    bathy[504,254] = 0.0
    bathy[502,254] = 0.0
    bathy[286,232] = 0.0
    bathy[740,687] = bathy[739,687] 
    bathy[422,236] = bathy[422,237] 
    bathy[279,238] = bathy[280,238] 

    mask1 = (bathy < 0.0)
    mask2 = (bathy > -5.0)
    mask = (mask1 & mask2)
    bathy = np.where(mask,-5.0,bathy)
    #bathy = np.where(bathy<-5800,-5800,bathy)

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
