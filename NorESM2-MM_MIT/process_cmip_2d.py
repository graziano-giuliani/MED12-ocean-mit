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
    indir = '../EC-Earth3-Veg/historical/zos'

varname = os.path.basename(indir)
listfiles = glob.glob(os.path.join(os.path.expanduser(indir),"*.nc"))

tmpfile = varname+"_tmp.nc"
for f in sorted(listfiles):
    rf,_ = os.path.splitext(os.path.basename(f))
    cdo.splityear(input=f, output=rf+'_year')
    for yf in sorted(glob.glob(rf+'_year'+'*.nc')):
        mf,_ = os.path.splitext(yf)
        cdo.splitmon(input=yf, output=mf+'_mon')
        os.unlink(yf)
        for m in sorted(glob.glob(mf+'_mon'+'*.nc')):
            oname = os.path.join(varname,os.path.basename(m))
            cdo.setmisstonn(input="-remapnn,mask.nc "+m,
                    output=tmpfile, options="-L -f nc4 -z zip_4")
            os.unlink(m)
            cdo.mul(input=tmpfile+" mask.nc",
                    output=oname, options="-L -f nc4 -z zip_4")
            os.unlink(tmpfile)
            print(oname)
print('Done')
