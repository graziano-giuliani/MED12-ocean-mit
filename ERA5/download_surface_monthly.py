#!/usr/bin/env python3

import os
import cdsapi

c = cdsapi.Client()

ys = 1950
ye = 2023

vname = { '2m_temperature' : 'tas',
          '2m_dewpoint_temperature': 'tdew',
          'total_precipitation' : 'pr',
          'surface_pressure' : 'ps',
          'runoff' : 'roff',
          'evaporation': 'evp',
          'surface_net_solar_radiation' : 'nssw',
          'surface_net_thermal_radiation' : 'nslw',
          '10m_u_component_of_wind' : 'uas',
          '10m_v_component_of_wind' : 'vas',
        }

for year in range(ys,ye+1):
    yy = '%04d' % year
    try:
        os.mkdir(yy)
    except OSError:
        pass
    for month in range(1,13):
        mm = '%02d' % month
        for var in vname:
            netcdf = os.path.join(str(year),(vname[var]+"_"+yy+'_'+mm+'.nc'))
            if not os.path.isfile(netcdf):
                c.retrieve(
                  'reanalysis-era5-single-levels-monthly-means',
                  {
                    'format': 'netcdf',
                    'variable': var,
                    'year': yy,
                    'month': mm,
                    'time': '00:00',
                    'product_type': 'monthly_averaged_reanalysis',
                  }, netcdf)
                os.system('compressnc '+netcdf)
            else:
                print('File '+netcdf+' already on disk.')
