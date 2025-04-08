#!/usr/bin/env python3

# Fill in the Atlantic and Black Sea from the ORAS5 monthly data
# Usage:
#        python3 merge_oras5.py ./ ../ORAS5_MIT


import sys
import os
from netCDF4 import Dataset
import numpy as np

mapvar = {
           'temperature' : 'votemper',
           'salinity'    : 'vosaline',
         }

ds = Dataset('mask.nc','r')
mask = ds.variables['mask'][:]
ds.close( )
mask = (mask == 0)

for year in range(1969,2016):
    if year > 2014:
        stream = '_OPER_'
    else:
        stream = '_CONS_'
    for month in range(1,13):
        y = "{0:04d}".format(year)
        m = "{0:02d}".format(month)
        for var in mapvar.keys( ):
            var1 = var
            var2 = mapvar[var]
            f1 = os.path.join(sys.argv[1],var1,
                    'medhymap_v2_2_'+y+'_ok_mon'+m+'.nc')
            if not os.path.exists(f1):
                print(f1+' is not present on disk.')
                continue
            f2 = os.path.join(sys.argv[2],var2,
                    var2+'_control_monthly_highres_3D_'+
                    y+m+stream+'v0.1.nc')
            if not os.path.exists(f2):
                print(f2+' is not present on disk.')
                continue
            print(f1 + ' <- ' + f2)
            ds1 = Dataset(f1,'a')
            v1 = ds1.variables[var1][:]
            ds2 = Dataset(f2,'r')
            v2 = ds2.variables[var2][:]
            v1 = np.where(mask,v2,v1)
            ds1.variables[var1][:] = v1
            ds2.close( )
            ds1.close( )
