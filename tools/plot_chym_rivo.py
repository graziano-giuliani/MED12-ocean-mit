#!/usr/bin/env python3

import os
import sys
import datetime
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

color1 = 'red'
color2 = 'blue'
color3 = 'salmon'
color4 = 'aqua'

obspath = '/leonardo_work/ICT25_ESP/OBS/RIVERS/RivDIS1.1'
datapath = '/leonardo_work/ICT25_ESP/COUPLED/coupled_new/loop2/CORDEX-CMIP6'
cordexpath = 'DD/MED-12/ICTP/ERA5/evaluation/r1i1p1f1/RegCM-ES1-1/v1-r1/day'
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
flist = os.path.join(datapath,cordexpath,varname,'*nc')
rivofile = xr.open_mfdataset(flist, decode_coords=all,
        concat_dim="time", combine='nested')

ymstart = rivofile.time[0].dt.strftime('%Y-%m').values
ymstop = rivofile.time[-1].dt.strftime('%Y-%m').values

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
    sigma2 = rivo[varname].resample(
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
