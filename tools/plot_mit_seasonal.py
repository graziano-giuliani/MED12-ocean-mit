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

figsize = (32,12)
levels = { "so"     : (30,31,32,33,34,34.25,34.5,34.75,35,
                       35.25,35.5,35.75,36,36.25,36.5,
                       36.75,37,37.25,37.5,37.75,38,
                       38.1,38.2,38.3,38.4,38.5,38.6,
                       38.7,38.8,38.9,39,39.1,39.2),
           "thetao" : np.linspace(4.0,28.0,25),
           "mlot"   : np.linspace(0.0,700,101),
           "hfns"   : None, # np.linspace(-200,200,51),
           "rsdo"   : None,
           "sltnf"  : None,
           "tau"    : None,
           "zos"    : np.linspace(-0.5,0.5,21),
         }

dpm = {'noleap': [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       '365_day': [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       'standard': [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       'gregorian': [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       'proleptic_gregorian': [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       'all_leap': [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       '366_day': [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
       '360_day': [0, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]}

def leap_year(year, calendar='standard'):
    """Determine if year is a leap year"""
    leap = False
    if ((calendar in ['standard', 'gregorian',
        'proleptic_gregorian', 'julian']) and
        (year % 4 == 0)):
        leap = True
        if ((calendar == 'proleptic_gregorian') and
            (year % 100 == 0) and
            (year % 400 != 0)):
            leap = False
        elif ((calendar in ['standard', 'gregorian']) and
                 (year % 100 == 0) and (year % 400 != 0) and
                 (year < 1583)):
            leap = False
    return leap

def get_dpm(time, calendar='standard'):
    """
    return a array of days per month corresponding to the months provided in `months`
    """
    month_length = np.zeros(len(time), dtype=np.int32)

    cal_days = dpm[calendar]

    for i, (month, year) in enumerate(zip(time.month, time.year)):
        month_length[i] = cal_days[month]
        if leap_year(year, calendar=calendar) and month == 2:
            month_length[i] += 1
    return month_length

def seasonal_gridlines(pax,i):
    if i == 0:
        pax.gridlines(draw_labels={'left':'y'},
                      dms=True, x_inline=False, y_inline=False)
    elif i == 2:
        pax.gridlines(draw_labels={'bottom':'x','left':'y'},
                      dms=True, x_inline=False, y_inline=False)
    elif i == 3:
        pax.gridlines(draw_labels={'bottom':'x'},
                      dms=True, x_inline=False, y_inline=False)
    else:
        pax.gridlines(draw_labels=False,
                      dms=True, x_inline=False, y_inline=False)

font = {'family' : 'sans',
        'weight' : 'normal',
        'size'   : 20}
matplotlib.rc('font', **font)

cbar_kws = dict(fraction=0.05, pad=0.06, shrink=0.85)

colors = { "so"     : cmocean.cm.haline,
           "thetao" : cmocean.cm.thermal,
           "mlot"   : cmocean.cm.deep,
           "hfns"   : cmocean.cm.balance,
           "rsdo"   : cmocean.cm.solar,
           "sltnf"  : cmocean.cm.diff,
           "tau"    : cmocean.cm.speed,
           "zos"    : cmocean.cm.balance,
         }

try:
    ncf = sys.argv[1]
    vname = os.path.basename(ncf).split('_')[0]
except:
    print('At least one filename must be provided!')
    sys.exit(-1)

flist = sys.argv[1:]
if "tau" in vname:
    ds = xr.open_mfdataset((x for x in flist if "tauu" in x),
            decode_coords=all, concat_dim="time", combine='nested')
    dsv = xr.open_mfdataset((x for x in flist if "tauv" in x),
            decode_coords=all, concat_dim="time", combine='nested')
    ds["tauv"] = dsv["tauv"]
    ds["tau"] = xr.ufuncs.sqrt(xr.ufuncs.square(ds["tauu"]) +
                               xr.ufuncs.square(ds["tauv"]))
    ds["tau"] = ds["tau"].assign_attrs(long_name = "Wind Stress")
    ds["tau"] = ds["tau"].assign_attrs(standard_name = "surface_wind_stress")
    pname = "tau"
    norm = matplotlib.colors.Normalize()
    norm.autoscale(np.linspace(0.0,0.5,10))
    sm = matplotlib.cm.ScalarMappable(cmap=colors["tau"], norm=norm)
    sm.set_array([])
elif vname == 'zos':
    fnu = list(x.replace('zos','uo') for x in flist)
    fnv = list(x.replace('zos','vo') for x in flist)
    ds = xr.open_mfdataset(flist, decode_coords=all,
            concat_dim="time", combine='nested')
    dsu = xr.open_mfdataset(fnu, decode_coords=all,
            concat_dim="time", combine='nested').isel(depth=0)
    dsv = xr.open_mfdataset(fnv, decode_coords=all,
            concat_dim="time", combine='nested').isel(depth=0)
    ds["uo"] = dsu["uo"]
    ds["vo"] = dsv["vo"]
    ds["spd"] = xr.ufuncs.sqrt(xr.ufuncs.square(ds["uo"]) +
                               xr.ufuncs.square(ds["vo"]))
    ds["spd"] = ds["spd"].assign_attrs(long_name = "Current")
    ds["spd"] = ds["spd"].assign_attrs(standard_name = "surface_current_speed")
    pname = vname
else:
    ds = xr.open_mfdataset(flist,decode_coords=all,
            concat_dim="time", combine='nested')
    pname = vname

try:
    calendar = ds.time.dt.calendar
except:
    calendar = "standard"

try:
    ymstart = ds.time[0].dt.strftime('%Y').values
    ymstop = ds.time[-1].dt.strftime('%Y').values
except:
    ymstart = '1979-08'
    ymstop = '1987-08'

month_length = xr.DataArray(get_dpm(ds.time.to_index(), calendar),
                            coords=[ds.time], name='month_length')
weights = ( month_length.groupby('time.season') / 
            month_length.astype(float).groupby('time.season').sum() )

if "depth" in ds[vname].dims:
    vp = (ds.isel(depth=0)*weights).groupby('time.season').sum(dim='time',
            skipna=False)
else:
    vp = (ds*weights).groupby('time.season').sum(dim='time',skipna=False)

fig, ax = plt.subplots(nrows=2, ncols=2, figsize=figsize,
        subplot_kw={'projection': ccrs.PlateCarree( ),
                    'facecolor' : 'grey',})

for i, season in enumerate(('DJF', 'MAM', 'JJA', 'SON')):
    pax = ax[i//2,i%2]
    if "tau" in vname:
        sp = vp.sel(season=season)
        x = sp["lon"][::10,::10]
        y = sp["lat"][::10,::10]
        u = sp["tauu"][::10,::10]
        v = sp["tauv"][::10,::10]
        c = sp["tau"][::10,::10]
        p = pax.quiver(x,y,u,v,c, transform = ccrs.PlateCarree( ),
                       cmap = colors["tau"])
        plt.colorbar(sm,ax=pax,extend="both",**cbar_kws)
        pax.set(title = vp[pname].long_name+' ['+vp[pname].units+
                '], season='+season)
        pax.add_feature(cfeature.LAND)
        pax.coastlines()
        seasonal_gridlines(pax,i)
    elif "zos" in vname:
        p = vp[vname].sel(season=season).plot(x = "lon", y = "lat",
                          transform = ccrs.PlateCarree( ),
                          ax = pax, robust=True,
                          extend = 'both',
                          levels = levels[vname],
                          cmap = colors[vname],
                          cbar_kwargs = cbar_kws)
        sp = vp.sel(season=season)
        x = sp["lon"]
        y = sp["lat"]
        u = sp["uo"]
        v = sp["vo"]
        c = sp["spd"]
        p1 = pax.streamplot(x, y, u, v, transform = ccrs.PlateCarree( ),
                          density=2.5,cmap=cmocean.cm.dense.reversed( ))
        seasonal_gridlines(pax,i)
    else:
        p = vp[vname].sel(season=season).plot(x = "lon", y = "lat",
                          transform = ccrs.PlateCarree( ),
                          ax = pax, robust=True,
                          extend = 'both',
                          levels = levels[vname],
                          cmap = colors[vname],
                          cbar_kwargs = cbar_kws)
        seasonal_gridlines(pax,i)
    pax.set_extent((-8,43,30,45))

plt.tight_layout()
fig.suptitle('Seasonal '+vp[pname].long_name+', '+ymstart+'-'+ymstop)
plt.savefig(pname+'_seasonal.png', bbox_inches='tight')
