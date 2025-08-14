#!/usr/bin/env python3

import os
import sys
import numpy as np
from netCDF4 import Dataset
from cdo import *

# Fine correction of bathinetric data

try:
    ifile = sys.argv[1]
    ofile = sys.argv[2]
except:
    ifile = "MIT_BATHY.nc"
    ofile = "BATHYMETRY.nc"

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
        if name not in ["elevation", "z"]:
            dst[name][:] = src[name][:]
        # copy variable attributes all at once via dictionary
        dst[name].setncatts(src[name].__dict__)
    try:
        bathy = src.variables['elevation'][:]
    except:
        bathy = src.variables['z'][:]

    # Remove greater than zero values
    bathy = np.where(bathy > 0.0, 0.0, bathy)
    # Remove not connected pixels
    nj,ni = np.shape(bathy)
    for i in range(1,ni-1):
       for j in range(1,nj-1):
           if bathy[j,i] < 0.0:
               if all(np.array((bathy[j-1,i],bathy[j+1,i],
                                bathy[j,i+1],bathy[j,i-1])) > -0.5):
                   bathy[j,i] = 0.0

#########################################################################
#########################################################################
##########  The Below lines are for the Mediterranean Sea ###############
#########################################################################
#########################################################################

    # Remove the Atlantic we don't need.
    bathy[0:25,0:62] = 0.0
    bathy[130:,0:62] = 0.0
    bathy[130:199,0:110] = 0.0
    bathy[200:,0:120] = 0.0
    bathy[300:,0:180] = 0.0

    # Remove a splotch in the desert
    bathy[0:10,500:] = 0.0

    # Remove a river mouth in the BlackSea
    bathy[317:,495:500] = 0.0

    # Wanted one Pixel Islands
    bathy[81,280] = 0.0   # Lampedusa
    bathy[166,298] = 0.0  # Capri
    bathy[171,280] = 0.0  # Ponza
    bathy[195,256] = 0.0  # Giglio
    bathy[203,249] = 0.0  # Elba

    # Close Bizerte Bay
    bathy[107,246] = 0.0
    bathy[107,247] = 0.0

    # Close Marmaris Bay
    bathy[112,467] = 0.0
    bathy[112,468] = 0.0

    # Close in Adana Bay
    bathy[110,556] = 0.0
    bathy[110,557] = 0.0

    # Sicily Channel increased depth
    bathy[127,315] = -250

    # Open up Corinth Gulf
    bathy[128,384] = -62
    bathy[131,390] = -62
    bathy[131,391] = -62
    bathy[132,388] = -62
    bathy[132,389] = -62
    bathy[132,390] = -62
    bathy[132,393] = -62

    # Close Ambracian Gulf
    bathy[141,381] = 0.0
    bathy[141,380] = 0.0
    bathy[142,380] = 0.0
    bathy[143,380] = 0.0
    bathy[142,379] = 0.0
    bathy[143,377] = 0.0
    bathy[142,378] = 0.0
    bathy[142,377] = 0.0
    bathy[141,377] = -25
    bathy[141,376] = -25
    bathy[142,376] = -25

    # Open up Eubean Gulf
    bathy[136,407] = -45
    bathy[137,407] = -45
    bathy[141,402] = -45
    bathy[142,402] = -45
    bathy[142,403] = -45

    # Open up Pagaseatic Gulf
    bathy[146,404] = -80
    bathy[146,405] = -70

    # Close Kallonis Gulf
    bathy[148,441] = 0.0
    bathy[149,441] = 0.0
    bathy[149,442] = 0.0

    # Limnos shape
    bathy[163,430] = 0.0

    # Dardanelles Strait
    bathy[169,441] = -40
    bathy[169,442] = -40
    bathy[169,443] = -55
    bathy[169,444] = -25
    bathy[170,444] = -26
    bathy[170,445] = -25
    bathy[170,446] = -45
    bathy[171,446] = -45
    bathy[172,446] = -25
    bathy[172,447] = -45
    bathy[173,447] = -45
    bathy[174,447] = 0.0

    # Bosphorus Strait
    bathy[187,473] = -65.0
    bathy[187,474] = -65.0
    bathy[188,474] = -65.0
    bathy[188,475] = -65.0
    bathy[190,474] = -45.0
    bathy[190,475] = -45.0
    bathy[191,475] = -45.0

    # Izmir
    bathy[165,442] = -65
    bathy[166,441] = -50

    # Izmit
    bathy[182,478] = -100
    bathy[182,483] = -25

    # Close Halkidiki
    bathy[169,411] = 0.0
    bathy[169,413] = 0.0
    bathy[166,406] = 0.0

    # Sardinia-Corsica Strait
    bathy[176,236] = -63
    bathy[176,237] = -65
    bathy[175,238] = -65

    # Close Cattaro Mouth
    bathy[203,348] = 0.0
    bathy[204,348] = 0.0
    bathy[204,349] = 0.0
    bathy[205,348] = 0.0

    # Close Posedarje
    bathy[233,308] = 0.0
    bathy[233,309] = 0.0
    bathy[238,302] = 0.0
    bathy[238,303] = 0.0
    bathy[239,302] = 0.0

    # Open for Rijeka
    bathy[249,292] = -48

#########################################################################
#########################################################################
####################    END MEDITERRANNEAN SEA MODIFS     ###############
#########################################################################
#########################################################################

    mask1 = (bathy < 0.0)
    mask2 = (bathy > -10.0)
    mask = (mask1 & mask2)
    bathy = np.where(mask,-10.5,bathy)

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
