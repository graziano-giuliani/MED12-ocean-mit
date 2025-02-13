#!/usr/bin/env python3

# Produce the initial condition from remapped and filled dataset of ORAS5
# Usage:
#         python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/votemper
#         python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/vosaline
#         python3 produce_ic.py ~/project/MITGCM/ORAS5_MED/sossheig


import os
import sys
import glob
from netCDF4 import Dataset
import numpy as np

startdate = 197908

files = glob.glob(os.path.expanduser(os.path.join(sys.argv[1],"*monthly*.nc")))
xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
dates = list(int(y[5]) for y in (x.split('_') for x in xfiles))

varname = xfiles[0].split('_')[0]

if varname in ["votemper", "vosaline"]:
    for o,f,d in zip(xfiles,files,dates):
        if d >= startdate:
            if not os.path.exists(o+".bin"):
                values = Dataset(f).variables[varname][:].data
                with open(o+".bin","wb") as fo:
                    values.astype('>f4').tofile(fo)
else: # sossheigh, keep only West boundary.
    for o,f,d in zip(xfiles,files,dates):
        if d >= startdate:
            if not os.path.exists(o+".bin"):
                values = Dataset(f).variables[varname][0,:,0].data
                with open(o+".bin","wb") as fo:
                    values.astype('>f4').tofile(fo)

outname = varname + '_' + repr(startdate) + '_' + repr(max(dates)) + '.bin'
try:
    os.unlink(outname)
except FileNotFoundError:
    pass
files = sorted(glob.glob(varname+"*.bin"))
fout = open(outname, "ab")
for f in files:
    with open(f, "rb") as fin:
        fout.write(fin.read( ))
    os.unlink(f)
