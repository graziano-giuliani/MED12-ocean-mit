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

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)
source = config["source_rbcs"]
start_year = config["start_year"]
start_month = config["start_month"]
end_year = config["end_year"]
end_month = config["end_month"]

start_month = start_month - 1
if start_month == 0:
    start_month = 12
    start_year = start_year - 1

startdate = start_year * 100 + start_month

mit_dt = config["mit_dt"]
mit_rbcs_dt = config["mit_rbcs_dt"]

increment = mit_rbcs_dt//mit_dt

if end_year > 0:
    enddate = end_year * 100 + end_month
else:
    enddate = -1

try:
    variables = config[source]['variables_rbcs'].split(' ')
except:
    sys.exit(0)
try:
    os.mkdir('rbcs')
except:
    pass

if source == 'oras5':
    try:
        oras5dir = sys.argv[1]
    except:
        oras5dir = "../ORAS5_MIT"
    for var in variables:
        gpath = os.path.join(oras5dir,var,"*monthly*.nc")
        files = sorted(glob.glob(os.path.expanduser(gpath)))
        xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
        dates = list(int(y[5]) for y in (x.split('_') for x in xfiles))
        if enddate < 0:
            enddate = dates[-1]
        itime = 0
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                mit_time_index = f'{itime:010}'
                outname = os.path.join('rbcs', var + '.' + 
                                       mit_time_index + '.data')
                try:
                    os.unlink(outname)
                except:
                    pass
                with open(outname, "wb") as fout:
                    values = Dataset(f).variables[var][:].data
                    values.astype('>f4').tofile(fout)
                itime = itime + increment
else:
    try:
        inpdir = sys.argv[1]
    except:
        print('Need input directory name')
        sys.exit(1)
    for var in variables:
        gpath = os.path.join(inpdir,var,"*year????_mon??.nc")
        files = sorted(glob.glob(os.path.expanduser(gpath)))
        xfiles = list(os.path.splitext(os.path.basename(x))[0] for x in files)
        dates = list(int(y[7][4:]+y[8][3:])
                     for y in (x.split('_') for x in xfiles))
        if enddate < 0:
            enddate = dates[-1]
        itime = 0
        for o,f,d in zip(xfiles,files,dates):
            if d >= startdate and d <= enddate:
                print(var+": "+repr(d))
                mit_time_index = f'{itime:010}'
                outname = os.path.join('rbcs', var + '.' + 
                                       mit_time_index + '.data')
                try:
                    os.unlink(outname)
                except:
                    pass
                with open(outname, "wb") as fout:
                    values = Dataset(f).variables[var][:].data
                    values.astype('>f4').tofile(fout)
                itime = itime + increment

print('Done')
