#!/usr/bin/env python3

# Remap, interpolate data into a domain defined by the mask.nc file.
# Usage:
#        python3 process_oras_2d.py [../ORAS5/sossheig]

import os
import sys
import glob
from cdo import *

cdo = Cdo()
try:
    if sys.argv[1][-1] == '/':
        indir = sys.argv[1][:-1]
    else:
        indir = sys.argv[1]
except:
    indir = '../ORAS5/sossheig'

varname = os.path.basename(indir)
listfiles = glob.glob(os.path.join(os.path.expanduser(indir),"*.nc"))

tmpfile = varname+"_tmp.nc"
for f in sorted(listfiles):
    oname = os.path.join(varname,os.path.basename(f))
    cdo.setmisstonn(input="-remapnn,mask.nc "+f,
            output=tmpfile, options="-L -f nc4 -z zip_4")
    cdo.mul(input=tmpfile+" mask.nc",
            output=oname, options="-L -f nc4 -z zip_4")
    os.unlink(tmpfile)
    print(oname)
print('Done')
