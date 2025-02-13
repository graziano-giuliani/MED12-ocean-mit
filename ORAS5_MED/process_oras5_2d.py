#!/usr/bin/env python3

# Remap, interpolate data into a domain defined by the mask.nc file.
# Usage:
#        python3 process_oras_2d.py ~/project/MITGCM/ORAS5/sossheigh

import os
import sys
import glob
from cdo import *

cdo = Cdo()
listfiles = glob.glob(os.path.join(os.path.expanduser(sys.argv[1]),"*.nc"))
for f in sorted(listfiles):
    cdo.setmisstonn(input="-remapnn,mask.nc "+f,
            output="tmp.nc", options="-L -f nc4 -z zip_4")
    cdo.mul(input="tmp.nc mask.nc", 
            output=os.path.basename(f), options="-L -f nc4 -z zip_4")
    os.unlink("tmp.nc")
    print(os.path.basename(f))
print('Done')
