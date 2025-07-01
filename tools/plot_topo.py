#!/usr/bin/env python3

import os
import sys
import cf_xarray as cfxr
import numpy as np
import xarray as xr
import cartopy.feature as cfeature
from cartopy import crs as ccrs
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.colors as colors

font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 18}
matplotlib.rc('font', **font)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
          'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
           cmap(np.linspace(minval, maxval, n)))
    return new_cmap

cmap = plt.get_cmap('terrain')
mycmap = truncate_colormap(cmap, 0.25, 0.9)

xr.set_options(keep_attrs=True)
infile = sys.argv[1]
fig, ax = plt.subplots(figsize=(32,22),
        subplot_kw={'projection': ccrs.PlateCarree( ),
                    'facecolor' : 'gray',})
ds = xr.open_dataset(infile)
cs = ax.pcolormesh(ds.xlon, ds.xlat, ds.topo,
        cmap=mycmap, vmin=0, vmax=2000,
        transform=ccrs.PlateCarree( ))
ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='purple')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, zorder=100, facecolor='blue')
ax.gridlines(draw_labels={"left":"y","bottom":"x"},
             dms=True, x_inline=False, y_inline=False)
cbar = fig.colorbar(cs, ax=ax,extend='both')
cbar.set_label('Atmosphere model topography [m]')
plt.tight_layout()
fig.suptitle('RegCM5 MED domain')
plt.show( )
