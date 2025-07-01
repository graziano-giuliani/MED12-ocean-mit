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
cbar_kws = dict(fraction= 0.05, pad=0.06)

levels = [0,10,20,30,50,75,100,200,300,500,750,1000,2000,3000,4000]

ds = xr.open_dataset(sys.argv[1])
fig, ax = plt.subplots(figsize=(32,12),
        subplot_kw={'projection': ccrs.PlateCarree( ),
                    'facecolor' : 'gray',})
p = xr.ufuncs.negative(ds.elevation).plot(x='lon',y='lat',
        ax = ax, transform = ccrs.PlateCarree( ),
        vmax=4000,vmin=0, cmap=cmocean.cm.deep, levels = levels,
        extend = 'both',cbar_kwargs = cbar_kws)
ax.gridlines(draw_labels=True,
             dms=True, x_inline=False, y_inline=False)
ax.coastlines()
ax.add_feature(cfeature.LAND, zorder=100, facecolor='white')
ax.set_extent((-8,43,30,45))
plt.tight_layout()
fig.suptitle('EMODnet Bathymetry - DTM 2024')

plt.show( )
