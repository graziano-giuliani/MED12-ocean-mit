#!/usr/bin/env python3

import os
import sys
import numpy as np
from netCDF4 import Dataset

ifile = sys.argv[1]
dsin = Dataset(ifile, mode='r')

#output file
ofile = sys.argv[2]
dsout = Dataset(ofile, "w", format="NETCDF4")

#Copy dimensions
for dname, the_dim in dsin.dimensions.items():
    dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)

# Copy variables
for v_name, varin in dsin.variables.items():
    if v_name == 'latitude':
        v_name = 'lat'
    if v_name == 'longitude':
        v_name = 'lon'
    outvar = dsout.createVariable(v_name, varin.datatype,
            varin.dimensions,zlib=True, fill_value=np.nan)
    outvar[:] = varin[:]
    outvar.setncatts(varin.__dict__)

# settings
dsout.variables['lat'].standard_name = 'latitude'
dsout.variables['lat'].units = 'degrees_north'
dsout.variables['lon'].standard_name = 'longitude'
dsout.variables['lon'].units = 'degrees_east'
dsout.variables['temperature'].units = 'Celsius'
dsout.variables['temperature_rmse'].units = 'Celsius'

# close the files
dsin.close( )
dsout.close()
