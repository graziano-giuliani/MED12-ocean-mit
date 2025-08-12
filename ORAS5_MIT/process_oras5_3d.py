#!/usr/bin/env python3

# Remap, fill and interpolate data into a domain defined by the mask.nc file.
# Vertical levels in the depth.nc file
# Usage:
#        python3 process_oras_3d.py ~/project/MITGCM/ORAS5/vosaline
#        python3 process_oras_3d.py ~/project/MITGCM/ORAS5/votemper

import os
import sys
import glob
from cdo import *

cdo = Cdo()
varname = os.path.basename(sys.argv[1])
listfiles = glob.glob(os.path.join(os.path.expanduser(sys.argv[1]),"*.nc"))
levels = cdo.showlevel(input="depth.nc", options="-s")
strlevels = " ".join((repr(x) for x in levels)).replace(" ",",")
for f in sorted(listfiles):
    oname = os.path.join(varname,os.path.basename(f))
    if not os.path.exists(oname):
        cdo.mul(input="mask.nc -intlevel,"+strlevels+
                  " -setmisstonn -vertfillmiss -remapnn,mask.nc "+f,
                output=oname, options="-L -f nc4 -z zip_4")
        print(oname)
print('Done')
