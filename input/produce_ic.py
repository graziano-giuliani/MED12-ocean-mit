#!/usr/bin/env python3

# Produce the boundary condition from remapped and filled dataset of ORAS5
# Usage:
#         python3 produce_bc.py [directory of processed ORAS5 data]

import os
import sys
import glob
from cdo import *
import yaml
from netCDF4 import Dataset
import numpy as np

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)
source = config["source_init"]
srcdir = config[source]["path"]
variables = config[source]["variables"].split( )

start_year = config["start_year"]
start_month = config["start_month"]
end_year = config["end_year"]
end_month = config["end_month"]
ic_decades = config["ic_decades"]

base = repr(start_year//100)
sdecade = (start_year//10) % 10 - (ic_decades//2 - 1) - (ic_decades % 2)
edecade = (start_year//10) % 10 + (ic_decades//2)
tmonth = f'{start_month:02d}'
if source == 'oras5':
    if sdecade == edecade:
        pattern = base+repr(sdecade)+"[0-9]"+tmonth
    else:
        pattern = base+"["+repr(sdecade)+'-'+repr(edecade)+"][0-9]"+tmonth
else:
    if sdecade == edecade:
        pattern = base+repr(sdecade)+"[0-9]"+"_ok_mon"+tmonth
    else:
        pattern = (base+"["+repr(sdecade)+'-'+
                repr(edecade)+"][0-9]"+"_ok_mon"+tmonth)

cdo = cdo.Cdo( )
for var in variables:
    if source == 'oras5':
        gpath = os.path.join(srcdir,var,var+"*_"+pattern+"_*.nc")
    else:
        gpath = os.path.join(srcdir,var,"*_"+pattern+".nc")
    files = " ".join(sorted(glob.glob(os.path.expanduser(gpath))))
    outname = (source + '_' + var + '_' + repr(start_year) + tmonth +
              '_' + repr(ic_decades) + '_decades.bin')
    fout = open(outname, "wb")
    values = cdo.timmean(input=" -mergetime "+files,returnArray=var).data
    values.astype('>f4').tofile(fout)

print('Done')
