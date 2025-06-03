#!/usr/bin/env python3

import sys
import os
import cmocean
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

#plt.rcParams['figure.figsize'] = (30.0, 10.0)
font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 22}
matplotlib.rc('font', **font)

subplot_kws = dict(projection = ccrs.PlateCarree( ),
                 facecolor = 'grey',
                )
cbar_kws = dict(fraction= 0.05, pad=0.06)

levels = { "so"     : (10,16,17,18,18.5,19.5,20,20.5,21,
                       21.5,22,22.5,23.0,23.5,24.0,24.5,
                       25.0,25.5,26,26.5,27.0,27.5,30,
                       31,32,33,34,34.25,34.5,34.75,35,
                       35.25,35.5,35.75,36,36.25,36.5,
                       36.75,37,37.25,37.5,37.75,38,
                       38.1,38.2,38.3,38.4,38.5,38.6,
                       38.7,38.8,38.9,39,39.1,39.2),
           "thetao" : np.linspace(10,36,53),
         }

colors = { "so"     : cmocean.cm.haline,
           "thetao" : cmocean.cm.thermal,
         }

for ncf in sys.argv[1:]:
    vbase = os.path.splitext(ncf)[0]
    vname = os.path.basename(ncf).split('_')[0]

    ds = xr.load_dataset(ncf)
    p = ds[vname][0,0,:].plot(x = "lon", y = "lat",
                              subplot_kws = subplot_kws,
                              cbar_kwargs = cbar_kws,
                              levels = levels[vname],
                              extend = 'both',
                              size = 10.0,
                              aspect = 3.2,
                              cmap = colors[vname])
    p.axes.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    p.axes.set_extent((-8,43,30,45))
    plt.savefig(os.path.basename(vbase)+'.png', bbox_inches='tight')
