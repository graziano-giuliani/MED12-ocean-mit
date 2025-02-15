#!/usr/bin/env python3

import os
import sys
from cdo import *

if not os.path.exists('grid_description.des'):
    print('Please prepare first the grid.')
    sys.exit(-1)

try:
    ifile = sys.argv[1]
except:
    ifile = 'Mediterranean_basin.nc'
try:
    ofile = sys.argv[2]
except:
    ofile = 'MIT_BATHY.nc'

cdo = cdo.Cdo( )

cdo.remapdis('grid_description.des,128', input=ifile,output=ofile)
