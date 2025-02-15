#!/usr/bin/env python3

# Transforms a single netCDF 3D file into a binary file
# Example:
#           python3 nc_to_bin.py votemper_monthly_highres_mean.nc

import os
import sys
from netCDF4 import Dataset

ifile = sys.argv[1]
xfile = os.path.splitext(os.path.basename(ifile))[0]
varname = xfile.split('_')[0]

if not os.path.exists(xfile+".bin"):
    values = Dataset(ifile).variables[varname][:].data
    with open(xfile+".bin","wb") as fo:
        values.astype('>f4').tofile(fo)
else:
    print('File '+xfile+".bin exists.")

print('Done.')
