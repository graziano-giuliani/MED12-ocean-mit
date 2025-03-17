#!/usr/bin/env python3

# Produce the External forcings from ERA5 data
# Usage:
#         python3 produce_extf.py [ERA5 interpolated data dir]

import os
import sys
import glob
from netCDF4 import Dataset
from cdo import *
import numpy as np

variables = [ "runoff", ]

cdo = Cdo( )

for var in variables:
    gpath = os.path.join('.',"orig","med*_mean.nc")
    files = sorted(glob.glob(os.path.expanduser(gpath)))
    xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
    dates = list(int(y[1]) for y in (x.split('_') for x in xfiles))

    startdate = dates[0]
    enddate = dates[-1]

    outname = ("CHYM_"+ var+ '_' + repr(startdate) +
                             '_' + repr(enddate) + '.bin')

    fout = open(outname, "wb")
    for f,d in zip(files,dates):
        if d >= startdate and d <= enddate:
            print(var+": "+repr(d))
            values = cdo.remapnn('../bathy/grid_description.des',
                input = "-selvar,"+var+' '+f,
                options = "-L -f nc4 -z zip_4 -b F32",
                returnArray = var).data
            values.astype('>f4').tofile(fout)
