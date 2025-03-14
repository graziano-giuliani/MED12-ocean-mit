#!/usr/bin/env python3

import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

plt.rcParams['figure.figsize'] = (18.0, 12.0)
font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 22}
matplotlib.rc('font', **font)

vbase = os.path.splitext(sys.argv[1])[0]
vname = sys.argv[1].split('.')[0]

levels = { "SALT" : [16.5,17.5,18.5,24,28,32,34,36,
                     36.5,37,37.5,38,38.5,39,39.5,40],
           "THETA" : np.linspace(16,30,8) }

ds = xr.load_dataset(sys.argv[1])
ds[vname][0,0,:].plot(x="lon",y="lat",levels=levels[vname],extend="both")
plt.savefig(vbase+'.png')
