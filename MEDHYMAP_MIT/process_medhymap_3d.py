#!/usr/bin/env python3

# Remap, fill and interpolate data into a domain defined by the mask.nc file.
# Vertical levels in the depth.nc file
# Usage:
#        python3 process_medhymap_3d.py temperature ../MEDHYMAP year
#        python3 process_medhymap_3d.py salinity ../MEDHYMAP year

import os
import sys
import glob
from cdo import *

cdo = Cdo()
varname = sys.argv[1]
try:
    listfiles = glob.glob(os.path.join(os.path.expanduser(sys.argv[2]),
                                   varname,'*_'+sys.argv[3]+'_*.nc'))
except:
    listfiles = glob.glob(os.path.join(os.path.expanduser(sys.argv[2]),
                                   varname,'*.nc'))
levels = cdo.showlevel(input="depth.nc", options="-s")
strlevels = " ".join((repr(x) for x in levels)).replace(" ",",")
tmpfile = varname+"_tmp.nc"
for f in sorted(listfiles):
    oname = os.path.join(varname,os.path.basename(f))
    if not os.path.exists(oname):
        cdo.intlevel(strlevels,
                input="-setmisstonn -vertfillmiss -remapnn,mask.nc "+f,
                output=tmpfile, options="-L -f nc4 -z zip_4")
        cdo.mul(input=tmpfile+" mask.nc",
                output=oname, options="-L -f nc4 -z zip_4")
        os.unlink(tmpfile)
        print(oname)
print('Done')
