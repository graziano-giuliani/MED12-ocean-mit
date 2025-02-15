#!/usr/bin/env python3

# Remap, interpolate data into a domain defined by the mask.nc file.
# Usage:
#        python3 process_era5_2d.py

import os
import glob
import yaml
from cdo import *

cpath = "config.yaml"
with open(cpath,"r") as f:
    config = yaml.safe_load(f)

cdo = Cdo()

e5path = config["era5_data"]
cvar = config["variables"]

for var in cvar.keys( ):
    os.makedirs(var,exist_ok=True)
    fname = cvar[var]["era5fname"]
    vname = cvar[var]["era5vname"]
    factor = str(cvar[var]["era5factor"])
    offset = str(cvar[var]["era5offset"])
    units = cvar[var]["units"]
    listfiles = glob.glob(os.path.join(e5path,"????",fname+"_*.nc"))
    for f in sorted(listfiles):
        oname = os.path.basename(f).replace(fname,var)
        ofile = os.path.join(var,oname)
        if not os.path.exists(ofile):
            newunit = " -setattribute,"+vname+"@units=\""+units+"\""
            newvar = " -mulc,"+factor+" -addc,"+offset
            cdo.chname(vname+","+var,
                input = newunit+newvar+" -remapnn,mask.nc "+f,
                output = ofile,
                options = "-L -f nc4 -z zip_4 -b F32")
            print(oname)
print('Done')
