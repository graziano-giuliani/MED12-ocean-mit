#!/usr/bin/env python3

import sys
import numpy as np
from netCDF4 import Dataset

tzero = 273.15

ps = Dataset(sys.argv[1],'r')
tdew = Dataset(sys.argv[2],'r')

out = Dataset(sys.argv[3],'w')

out.setncatts(ps.__dict__)

for name, dimension in ps.dimensions.items():
    out.createDimension(name, (len(dimension) 
        if not dimension.isunlimited() else None))

for name, variable in ps.variables.items():
    if name not in 'sp':
        if "expver" in name:
            continue
        x = out.createVariable(name, variable.datatype, variable.dimensions)
        # copy variable attributes all at once via dictionary
        out[name].setncatts(ps[name].__dict__)
        out[name][:] = ps[name][:]
    else:
        x = out.createVariable("sh", variable.datatype, variable.dimensions)
        d2m = tdew["d2m"][:]
        sp = ps["sp"][:]
        # Use Tetens formula with better fit and extension for low temperature
        satp = np.where(d2m >= tzero,
                610.78 * np.exp(17.2693882*(d2m-tzero)/(d2m-35.86)),
                610.78 * np.exp(21.875*(d2m-tzero)/(d2m-7.66)))
        mx = 0.62195691 * satp/(sp-satp)
        out["sh"].units = "kg/kg"
        out["sh"].long_name = "Surface Specific Humidity"
        out["sh"].notes = "Computed from dewpoint temp dewt and pressure sp"
        out["sh"].algorithm1 = "satp = 610.78*exp(a*(dewt-273.15)/(dewt-b));"
        out["sh"].algorithm2 = " with t >= 273.15 ; a = 17.2693882, b=35.86;"
        out["sh"].algorithm3 = "      t <  273.15 ; a = 21.875,     b= 7.66;"
        out["sh"].algorithm4 = "sh = 0.62195691*satp/(sp-satp);"
        out["sh"][:] = mx
