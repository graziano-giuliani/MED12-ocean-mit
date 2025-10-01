#!/usr/bin/env python3

import os
import sys
import datetime
import dateutil
import uuid
import numpy as np
import f90nml
from netCDF4 import Dataset

# Need to be setup.
domain = 'MED-12'
myinst = 'ICTP'
ginst = 'ECMWF'
gmodel = 'ERA5'
gmemb = 'r1i1p1f1'
experiment = 'evaluation'
start_simulation = '1979-08-01 00:00:00'
outpath = '.'
# End Setup

names = { 'dis'        : { 'esgf_name'     : 'rivo',
                           'standard_name' : 'water_flux_to_downstream ',
                           'long_name'     : 'River Discharge',
                           'units'         : 'm3 s-1',
                           'coordinates'   : 'lat lon',
                          },
        }

for ncfile in sys.argv[1:]:
    dsin = Dataset(ncfile, 'r')
    for var in names.keys( ):
        if not var in dsin.variables:
            continue

        infname = names[var]['esgf_name']
        ftime = dsin.variables['time'][:]
        stime = int(ftime[0])
        etime = int(ftime[-1])
        s_ymd = (datetime.datetime.fromisoformat(start_simulation)+
                 datetime.timedelta(days=stime))
        e_ymd = (datetime.datetime.fromisoformat(start_simulation)+
                 datetime.timedelta(days=etime))

        lon = dsin.variables['lon'][:]
        lat = dsin.variables['lat'][:]

        opath = os.path.join(outpath,'CORDEX-CMIP6','DD',domain,myinst,
                gmodel,experiment,gmemb,'RegCM-ES1-1','v1-r1','day',
                infname)
        os.makedirs(opath,exist_ok=True)
        ncfile = os.path.join(opath, infname + '_' + domain + '_' + gmodel +
                '_' + experiment + '_' + gmemb + '_' + myinst +
                '_RegCM-ES1-1_v1-r1_' + s_ymd.strftime('%Y%m%d') + '-' +
                e_ymd.strftime('%Y%m%d') + '.nc')
        dsout = Dataset(ncfile,'w')
        for name, dimension in dsin.dimensions.items():
            dsout.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None))
        xlon = dsout.createVariable('lon','f8',('lat','lon'))
        xlon.standard_name = 'longitude'
        xlon.long_name = 'Longitude'
        xlon.units = 'degrees_east'
        xlat = dsout.createVariable('lat','f8',('lat','lon'))
        xlat.standard_name = 'latitude'
        xlat.long_name = 'Latitude'
        xlat.units = 'degrees_north'
        xtime = dsout.createVariable('time','f8',('time'))
        xtime.setncatts(dsin.variables['time'].__dict__)
        xvar = dsout.createVariable(infname,'f4',('time','lat','lon'),
                compression='zlib',complevel=6,significant_digits=4)
        xvar.standard_name = names[var]['standard_name']
        xvar.long_name = names[var]['long_name']
        xvar.units = names[var]['units']
        xvar.coordinates = names[var]['coordinates']

        xlon[:] = lon
        xlat[:] = lat

        now = datetime.datetime.now( ).isoformat( )
        dsout.Conventions = "CF-1.11"
        dsout.creation_date = now
        dsout.tracking_id = 'hdl:21.14103/'+str(uuid.uuid1( ))
        dsout.description = domain+' simulation'
        dsout.title = 'Coupled RegCM-ES1-1 simulation. Ocean Component is MITgcm checkpoint69. Output prepared for CORDEX experiment'
        dsout.activity_id = 'CORDEX'
        dsout.contact = 'ggiulian@ictp.it'
        dsout.experiment_id = experiment
        dsout.domain = 'Mediterranean'
        dsout.domain_id = domain
        dsout.grid = 'NEMO ORCA tripolar resolution 1/12 deg'
        if experiment == 'evaluation':
            dsout.driving_experiment = 'reanalysis simulation of the recent past'
        elif experiment == 'historical':
            dsout.driving_experiment = 'scenario simulation of the recent past'
        else:
            dsout.driving_experiment = 'future scenario simulation'
        dsout.driving_experiment_id = experiment
        dsout.driving_institution_id = ginst
        dsout.driving_source_id = gmodel
        dsout.driving_variant_label = gmemb
        dsout.frequency = 'day'
        dsout.table_id = 'Table day'
        dsout.institution = 'The Abdus Salam International Centre for Theoretical Physics, Trieste, Italy'
        dsout.institution_id = myinst
        dsout.license = 'https://cordex.org/data-access/cordex-cmip6-data/cordex-cmip6-terms-of-use'
        dsout.mip_era = 'CMIP6'
        dsout.product = 'model-output'
        dsout.project_id = 'CORDEX-CMIP6'
        dsout.source = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5.0, MITgcm v6.9d and CHyM (2025)'
        dsout.source_id = 'RegCM-ES1-1'
        dsout.source_type = 'AORCM'
        dsout.realm = 'land'
        dsout.version_realization = 'v1-r1'
        dsout.version_realization_info = 'none'
        dsout.activity_participation = 'DD'
        dsout.cohort = 'Registered'
        dsout.further_info_url = 'https://www.medcordex.eu/Med-CORDEX-2_baseline-runs_protocol.pdf'
        dsout.label = 'RegCM-ES1-1'
        dsout.label_extended = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5.0, MITgcm v6.9d and CHyM (2025)'
        dsout.release_year = '2025'
        dsout.title = 'ICTP Regional Climatic Coupled model V1.1'
        dsout.references = 'https://github.com/graziano-giuliani/MED12-ocean-mit'
        dsout.model_revision = '1.1'
        dsout.history = now+': Created by RegCM-ES1-1 model run'

        att1 = f90nml.read('chym.namelist')
        for a in att1['iniparam'].keys( ):
            dsout.setncattr(a, str(att1['iniparam'][a]))

        for it in range(len(dsin.dimensions['time'])):
            xtime[it] = ftime[it]
            xvar[it,Ellipsis] = dsin.variables[var][it,Ellipsis]

        dsout.close( )

    dsin.close( )
