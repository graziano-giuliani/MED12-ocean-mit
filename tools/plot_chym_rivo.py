#!/usr/bin/env python3

import os
import sys
import datetime
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

obspath = '/leonardo_work/ICT25_ESP/OBS/RIVERS/RivDIS1.1'
datapath = '/leonardo_work/ICT25_ESP/COUPLED/coupled/loop2/CORDEX-CMIP6'
cordexpath = 'DD/MED-12/ICTP/ERA5/evaluation/r1i1p1f1/RegCM-ES1-1/v1-r1/day'
varpath = 'rivo'

riverlist = ( { 'name' : 'Danube',
                'iloc' : 426,
                'jloc' : 314 },
              { 'name' : 'Po',
                'iloc' : 221,
                'jloc' : 279},
              { 'name' : 'Ebro',
                'iloc' : 86,
                'jloc' : 195},
              { 'name' : 'Rhone',
                'iloc' : 133,
                'jloc' : 243},
              { 'name' : 'Dnieper',
                'iloc' : 456,
                'jloc' : 352},
              { 'name' : 'Don',
                'iloc' : 535,
                'jloc' : 388},
              { 'name' : 'Maritsa',
                'iloc' : 389,
                'jloc' : 214},
              { 'name' : 'Tiber',
                'iloc' : 224,
                'jloc' : 221},
              { 'name' : 'Kizil',
                'iloc' : 506,
                'jloc' : 243},
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
flist = os.path.join(datapath,cordexpath,varpath,'*nc')
rivofile = xr.open_mfdataset(flist, decode_coords=all,
        concat_dim="time", combine='nested')

ymstart = rivofile.time[0].dt.strftime('%Y-%m').values
ymstop = rivofile.time[-1].dt.strftime('%Y-%m').values

for river in riverlist:
    river_stations = stations[stations.RIVER==river['name']]
    mouth = river_stations[river_stations['NXT_PNT'].apply(str.isspace)]
    pointid = mouth.POINTID.values[0]
    data_river = rivdis[rivdis.POINTID == pointid]
    ystart = int(rivdis['YEAR'].min( ))
    ystop = int(rivdis['YEAR'].max( ))
    month_mean = data_river.groupby('MONTH').mean( )

    rivo = rivofile.isel(lon=river['iloc'],
                         lat=river['jloc']).groupby('time.month').mean()

    plt.plot(rivo.month,
         month_mean['DISCHRG'].values, label='RivDIS V1.1 - Average '+
         repr(ystart)+'-'+repr(ystop))
    plt.plot(rivo.month, rivo.rivo, label='CHyM MODEL ('+
            ymstart+' to '+ymstop+')')
    plt.xlabel('Month')
    plt.ylabel('Discharge [m3 s-1]')
    plt.title(river['name']+' at '+mouth.STATION.values[0])
    plt.legend( )
    plt.savefig(river['name']+'.png')
    plt.close( )
