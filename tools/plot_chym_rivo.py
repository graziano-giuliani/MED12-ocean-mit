#!/usr/bin/env python3

import os
import sys
import pathlib
import itertools
import datetime
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

color1 = 'red'
color2 = 'blue'
color3 = 'salmon'
color4 = 'aqua'

paths = [ 'initial', 'loop?' ]
obspath = '/leonardo_work/ICT26_ESP/OBS/RIVERS/RivDIS1.1'

varname = 'rivo'

riverlist = ( { 'name' : 'Danube',
                'iloc' : 413,
                'jloc' : 312 },
              { 'name' : 'Po',
                'iloc' : 213,
                'jloc' : 279},
              { 'name' : 'Ceyhan',
                'iloc' : 505,
                'jloc' : 147},
              { 'name' : 'Ebro',
                'iloc' : 84,
                'jloc' : 197},
              { 'name' : 'Rhone',
                'iloc' : 131,
                'jloc' : 250},
              { 'name' : 'Dnieper',
                'iloc' : 483,
                'jloc' : 392},
              { 'name' : 'Don',
                'iloc' : 548,
                'jloc' : 399},
              { 'name' : 'Maritsa',
                'iloc' : 380,
                'jloc' : 239},
              { 'name' : 'Tiber',
                'iloc' : 226,
                'jloc' : 222},
              { 'name' : 'Kizil',
                'iloc' : 516,
                'jloc' : 233},
            )

stations = pd.read_csv(os.path.join(obspath,'comp','STATION.DAT'),
                       sep='|', skiprows=1)
rivdis = pd.read_csv(os.path.join(obspath,'data','RIVDIS.DAT'),
                     sep='|', skiprows=1)
rivdis['YEAR'] = pd.to_numeric(rivdis['YEAR'],
        downcast='integer', errors='coerce')
rivdis['MONTH'] = pd.to_numeric(rivdis['MONTH'],
        downcast='integer', errors='coerce')
rivdis['DISCHRG'] = pd.to_numeric(rivdis['DISCHRG'],
        downcast='float', errors='coerce')

sdir = pathlib.Path(sys.argv[1])
patterns = ( os.path.join(x,'CORDEX-CMIP6','**',
                        varname,varname+'*.nc') for x in paths )
matched_paths = list(
      itertools.chain.from_iterable(sdir.glob(pattern)
      for pattern in patterns) )

rivofile = xr.open_mfdataset(sorted(matched_paths), concat_dim="time",
      combine='nested', data_vars='minimal', compat='no_conflicts')

ymstart = min(rivofile.time).dt.strftime('%Y-%m').values
ymstop = max(rivofile.time).dt.strftime('%Y-%m').values

fig, axs = plt.subplots(2,5,figsize=(32,10))

for river, ax in zip(riverlist, axs.reshape(-1)):
    river_stations = stations[stations.RIVER==river['name']]
    mouth = river_stations[river_stations['NXT_PNT'].apply(str.isspace)]
    pointid = mouth.POINTID.values[0]
    data_river = rivdis[rivdis.POINTID == pointid]
    ystart = int(rivdis['YEAR'].min( ))
    ystop = int(rivdis['YEAR'].max( ))
    measure = data_river.groupby('MONTH')
    data1 = measure['DISCHRG'].mean( ).values
    sigma1 = measure['DISCHRG'].std( ).values

    rivo = rivofile.isel(lon=river['iloc'], lat=river['jloc'])
    data2 = rivo[varname].groupby('time.month').mean( ).values
    sigma2 = rivo[varname].sortby('time').resample(
            time='MS').mean( ).groupby('time.month').std( ).values
    months = np.linspace(1,12,12)

    ax.plot(months, data1, label='RivDIS v1.1 ('+
         repr(ystart)+'-'+repr(ystop)+')', color=color1)
    ax.plot(months, data2, label='CHyM MODEL ('+
            ymstart+' to '+ymstop+')',color=color2)
    ax.fill_between(months, data1-sigma1, data1+sigma1,
                    facecolor=color3,alpha=0.5)
    ax.fill_between(months, data2-sigma2, data2+sigma2,
                    facecolor=color4,alpha=0.5)
    ax.legend( )
    ax.set_xticks(months,['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  rotation=45)
    ax.set_title(river['name']+' at '+mouth.STATION.values[0])
    ax.set_ylabel('Discharge [m3 s-1]')

plt.tight_layout( )
plt.savefig('Med-CHyM.png')
plt.close( )
