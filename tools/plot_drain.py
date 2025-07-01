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

xr.set_options(keep_attrs=True)
font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 18}
matplotlib.rc('font', **font)
cbformat = matplotlib.ticker.ScalarFormatter()
cbformat.set_powerlimits((-2,2))
cbar_kws = dict(fraction= 0.05, pad=0.06, format=cbformat)

ds = xr.open_dataset(sys.argv[1])
fig, ax = plt.subplots(figsize=(24,24),
        subplot_kw={'projection': ccrs.PlateCarree( ),
                    'facecolor' : 'gray',})
p = ds.dra.plot(x='lon',y='lat',
        ax = ax, transform = ccrs.PlateCarree( ),
        vmin=5000, vmax=50000, cmap=cmocean.cm.rain,
        extend = 'both',cbar_kwargs = cbar_kws)
ax.gridlines(draw_labels=True,
             dms=True, x_inline=False, y_inline=False)
ax.set_extent((-6,46,28,55))
ax.coastlines()
ax.add_feature(cfeature.OCEAN, zorder=100, facecolor='white')
plt.tight_layout()
fig.suptitle('CHyM drainage network')

plt.show( )
