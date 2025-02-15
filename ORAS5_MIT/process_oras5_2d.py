#!/usr/bin/env python3

# Remap, interpolate data into a domain defined by the mask.nc file.
# Usage:
#        python3 process_oras_2d.py ~/project/MITGCM/ORAS5/sossheigh

import os
import sys
import glob
from cdo import *

cdo = Cdo()
varname = os.path.basename(sys.argv[1])
listfiles = glob.glob(os.path.join(os.path.expanduser(sys.argv[1]),"*.nc"))
for f in sorted(listfiles):
    oname = os.path.join(varname,os.path.basename(f))
    cdo.setmisstonn(input="-remapnn,mask.nc "+f,
            output="tmp.nc", options="-L -f nc4 -z zip_4")
    cdo.mul(input="tmp.nc mask.nc", 
            output=oname, options="-L -f nc4 -z zip_4")
    os.unlink("tmp.nc")
    print(oname)
print('Done')
