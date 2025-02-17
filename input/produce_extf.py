#!/usr/bin/env python3

# Produce the External forcings from ERA5 data
# Usage:
#         python3 produce_extf.py [ERA5 interpolated data dir]

import os
import sys
import yaml
import glob
from netCDF4 import Dataset
import numpy as np

try:
    era5dir = sys.argv[1]
except:
    era5dir = "../ERA5"

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)
start_year = config["start_year"]
end_year = config["end_year"]
end_month = config["end_month"]

# ERA5 reference date is middle month.
start_month = config["start_month"] - 1
if start_month == 0:
    start_year = start_year - 1
    start_month = 12

startdate = start_year * 100 + start_month
if end_year > 0:
    enddate = end_year * 100 + end_month
else:
    enddate = -1

variables = [ "apressure", "aqh", "atemp", "evap", "lwflux", "precip",
              "runoff", "swflux", "uwind", "vwind" ]

for var in variables:
    gpath = os.path.join(era5dir,var,"*_????_??.nc")
    files = sorted(glob.glob(os.path.expanduser(gpath)))
    xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
    dates = list(int(y[1]+y[2]) for y in (x.split('_') for x in xfiles))

    if enddate < 0:
        enddate = dates[-1]

    outname = ("ERA5_"+ var+ '_' + repr(startdate) +
                             '_' + repr(enddate) + '.bin')
    try:
        os.unlink(oname)
    except:
        pass

    fout = open(outname, "ab")
    for f,d in zip(files,dates):
        if d >= startdate and d <= enddate:
            print(var+": "+repr(d))
            values = Dataset(f).variables[var][:].data
            values.astype('>f4').tofile(fout)
