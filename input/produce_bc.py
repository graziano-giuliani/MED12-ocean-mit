#!/usr/bin/env python3

# Produce the boundary condition from remapped and filled dataset of ORAS5
# Usage:
#         python3 produce_bc.py [directory of processed ORAS5 data]

import os
import sys
import glob
import yaml
from netCDF4 import Dataset
import numpy as np

try:
    oras5dir = sys.argv[1]
except:
    oras5dir = "../ORAS5_MIT"

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)
start_year = config["start_year"]
start_month = config["start_month"]
end_year = config["end_year"]
end_month = config["end_month"]

startdate = start_year * 100 + start_month
if end_year > 0:
    enddate = end_year * 100 + end_month
else:
    enddate = -1

variables = [ "votemper", "vosaline", "sossheig" ]

for var in variables:
    gpath = os.path.join(oras5dir,var,"*monthly*.nc")
    files = sorted(glob.glob(os.path.expanduser(gpath)))
    xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
    dates = list(int(y[5]) for y in (x.split('_') for x in xfiles))

    if enddate < 0:
        enddate = dates[-1]

    outname = var + '_' + repr(startdate) + '_' + repr(enddate) + '.bin'
    try:
        os.unlink(outname)
    except:
        pass

    fout = open(outname, "wb")
    if var in ["votemper", "vosaline"]: # full 3d field
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                values = Dataset(f).variables[var][:].data
                values.astype('>f4').tofile(fout)
    else: # sossheig, keep only West boundary.
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                values = Dataset(f).variables[var][0,:,0].data
                values.astype('>f4').tofile(fout)
    if var in ["votemper", "vosaline"]: # full 3d field
        for o,f,d in zip(xfiles,files,dates):
            if d == startdate:
                print(var+": "+repr(d))
                values = Dataset(f).variables[var][:].data
                values.astype('>f4').tofile(fout)
    else: # sossheig, keep only West boundary.
        for o,f,d in zip(xfiles,files,dates):
            if d == startdate:
                print(var+": "+repr(d))
                values = Dataset(f).variables[var][0,:,0].data
                values.astype('>f4').tofile(fout)

print('Done')
