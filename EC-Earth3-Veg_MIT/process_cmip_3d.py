#!/usr/bin/env python3

# Remap, fill and interpolate data into a domain defined by the mask.nc file.
# Vertical levels in the depth.nc file
# Usage:
#        python3 process_oras_3d.py ../ORAS5/vosaline
#        python3 process_oras_3d.py ../ORAS5/votemper

import os
import sys
import glob
from cdo import *

cdo = Cdo()
try:
    if sys.argv[1][-1] == '/':
        indirs = [sys.argv[1][:-1],]
    else:
        indirs = [sys.argv[1],]
except:
    indirs = ['../EC-Earth3-Veg/historical/so',
              '../EC-Earth3-Veg/historical/thetao']

for ind in indirs:
    print('Processing ',ind)
    varname = os.path.basename(ind)
    listfiles = glob.glob(os.path.join(os.path.expanduser(ind),"*.nc"))
    levels = cdo.showlevel(input="depth.nc", options="-s")
    strlevels = " ".join((repr(x) for x in levels)).replace(" ",",")
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
                if not os.path.exists(oname):
                    cdo.intlevel(strlevels,
                        input="-setmisstonn -vertfillmiss -remapnn,mask.nc "+m,
                        output=tmpfile, options="-L -f nc4 -z zip_4")
                    cdo.mul(input=tmpfile+" mask.nc",
                        output=oname, options="-L -f nc4 -z zip_4")
                    os.unlink(tmpfile)
                os.unlink(m)
                print(oname)
print('Done')
