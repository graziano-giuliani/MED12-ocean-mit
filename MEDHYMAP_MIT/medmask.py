#!/usr/bin/env python3

import sys
from netCDF4 import Dataset
import numpy as np

ds = Dataset(sys.argv[1],'a')

mask = ds.variables['mask'][:]

mask[:,0:63] = 0
mask[170:,444:] = 0
ds.variables['mask'][:] = mask

ds.close( )
