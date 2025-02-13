#!/usr/bin/env python3

# Produce the External forcings from ERA5 data
# Usage:
#         python3 produce_ic.py ~/project/MITGCM/ERA5/evap

import os
import sys
import glob
from netCDF4 import Dataset
import numpy as np

startdate = 197908

files = glob.glob(os.path.expanduser(os.path.join(sys.argv[1],"*_????_??.nc")))
xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
dates = list(int(y[1]+y[2]) for y in (x.split('_') for x in xfiles))

varname = xfiles[0].split('_')[0]
outname = ("ERA5_"+ varname + '_' +
           repr(startdate) + '_' + repr(max(dates)) + '.bin')

fout = open(outname, "ab")
for f,d in zip(files,dates):
   if d >= startdate:
       values = Dataset(f).variables[varname][:].data
       values.astype('>f4').tofile(fout)
