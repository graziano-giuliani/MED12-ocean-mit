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

font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 22}
matplotlib.rc('font', **font)

subplot_kws = dict(projection = ccrs.PlateCarree( ),
                 facecolor = 'grey',
                )

cbar_kws = dict(fraction= 0.05, pad=0.06)

levels = { "zos"     : np.linspace(-0.5,0.5,21),
         }

colors = { "zos"    : cmocean.cm.balance,
         }

for ncf in sys.argv[1:]:
    vbase = os.path.splitext(ncf)[0]
    dbase = os.path.dirname(ncf)
    pieces = os.path.basename(ncf).split('_')
    vname = pieces[0]
    ncu = os.path.join(os.path.dirname(dbase),'uo','uo_'+'_'.join(pieces[1:]))
    ncv = os.path.join(os.path.dirname(dbase),'vo','vo_'+'_'.join(pieces[1:]))

    dsc = xr.open_mfdataset((ncf,ncu,ncv),combine='nested',compat='override')
    dsc = dsc.isel(time=0,depth=0)
    p = dsc[vname].plot(x = "lon", y = "lat",
                        subplot_kws = subplot_kws,
                        cbar_kwargs = cbar_kws,
                        size = 10.0, aspect = 3.2,
                        levels = levels[vname],
                        extend = 'both', cmap = colors[vname])
    dsc["speed"] = np.sqrt(dsc.uo**2 + dsc.vo**2)
    dsc["speed"] = dsc["speed"].assign_attrs(long_name = "Current Speed",
                                             units = "m s-1")
    p1 = dsc.plot.streamplot(x = "lon", y = "lat",
                             u = "uo", v = "vo",
                             hue = "speed", hue_style = "continuous",
                             cmap = cmocean.cm.dense.reversed( ),
                             cbar_kwargs = { "location" : "bottom",
                                             "shrink" : 0.60,
                                             "pad"    : 0.06,
                                             "fraction" : 0.05,
                                             "aspect" : 40.0,},
                             density=5.0, linewidth=1.0)
    p.axes.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
    p.axes.set_extent((-8,43,30,45))
    plt.savefig(os.path.basename(vbase)+'.png', bbox_inches='tight')
    plt.close("all")
