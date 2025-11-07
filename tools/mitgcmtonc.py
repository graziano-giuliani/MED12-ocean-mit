#!/usr/bin/env python3

import os
import sys
import datetime
import dateutil
import glob
import uuid
import numpy as np
import xarray as xr
from MITgcmutils import mds
import f90nml

timestep = 150
start_simulation = "1979-08-01 00:00:00"
calendar = "standard"
domain = 'MED-12'
myinst = 'ICTP'
ginst = 'ECMWF'
gmodel = 'ERA5'
gmemb = 'r1i1p1f1'
experiment = 'evaluation'
outpath = '.'
# End Setup

metainfo = mds.parsemeta('hFacC.meta')
NX = metainfo['dimList'][0]
NY = metainfo['dimList'][3]
NZ = metainfo['dimList'][6]
avpickup = glob.glob('pickup.*.meta')[0]
metainfo = mds.parsemeta(avpickup)
NFPICKUP = metainfo['nrecords'][0]
pickup_flds = metainfo['fldList']

zc = - np.fromfile('RC.data', '>f4')
zf = - np.fromfile('RF.data', '>f4')
zz = np.empty((len(zc),2), dtype='f4')
zz[:,0] = zf[0:-1]
zz[:,1] = zf[1:]

names = { 'SALT'        : { 'esgf_name'     : 'so',
                            'standard_name' : 'sea_water_absolute_salinity',
                            'long_name'     : 'Ocean salinity',
                            'units'         : 'g kg-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'THETA'       : { 'esgf_name'     : 'thetao',
                            'standard_name' : 'sea_water_potential_temperature',
                            'long_name'     : 'Ocean potential temperature',
                            'units'         : 'degree_C',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'RHO'         : { 'esgf_name'     : 'rhopoto',
                            'standard_name' : 'sea_water_potential_density',
                            'long_name'     : 'Density anomaly',
                            'units'         : 'kg m-3',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'ELEVATION'   : { 'esgf_name'     : 'zos',
                            'standard_name' : 'sea_surface_height_above_geoid',
                            'long_name'     : 'Sea Surface Elevation Anomaly',
                            'units'         : 'm',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'HFLUX'       : { 'esgf_name'     : 'hfns',
                            'standard_name' : 'surface_net_heat_flux_in_sea_water',
                            'long_name'     : 'Net Heat Flux',
                            'units'         : 'W m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'oceFWflx'    : { 'esgf_name'     : 'sltnf',
                            'standard_name' : 'net_freshwater_flux',
                            'long_name'     : 'Net Surface Freshwater Flux into the Ocean',
                            'units'         : 'kg/m^2/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFevap'     : { 'esgf_name'     : 'evap',
                            'standard_name' : 'evaporation_flux',
                            'long_name'     : 'Evaporation flux from the Ocean',
                            'units'         : 'm/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFhl'       : { 'esgf_name'     : 'hfls',
                            'standard_name' : 'latent_heat_flux',
                            'long_name'     : 'Latent heat flux into the Ocean',
                            'units'         : 'W/m2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFhs'       : { 'esgf_name'     : 'hfss',
                            'standard_name' : 'sensible_heat_flux',
                            'long_name'     : 'Sensible heat flux into the Ocean',
                            'units'         : 'W/m2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFpreci'    : { 'esgf_name'     : 'pr',
                            'standard_name' : 'precipitation_flux',
                            'long_name'     : 'precipitation flux into the Ocean',
                            'units'         : 'kg/m2/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          #'EXFempmr'    : { 'esgf_name'     : 'fsltnf',
          #                  'standard_name' : 'net_forcing_upward_freshwater_flux',
          #                  'long_name'     : 'Forcing Net upward freshwater flux',
          #                  'units'         : 'm/s',
          #                  'dimensions'    : 2,
          #                  'stagger'       : 'c',
          #                  'coordinates'   : 'lat lon',
          #                },
          #'EXFroff'     : { 'esgf_name'     : 'siflfwdrain',
          #                  'standard_name' : 'water_flux_into_sea_water_due_to_surface_drainage',
          #                  'long_name'     : 'Forcing River freshwater flux',
          #                  'units'         : 'm/s',
          #                  'dimensions'    : 2,
          #                  'stagger'       : 'c',
          #                  'coordinates'   : 'lat lon',
          #                },
          'MLD'         : { 'esgf_name'     : 'mlot',
                            'standard_name' : 'ocean_mixed_layer_thickness',
                            'long_name'     : 'Ocean Mixed Layer Thickness',
                            'units'         : 'm',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          #'SFLUX'       : { 'esgf_name'     : 'osalttend',
          #                  'standard_name' : 'tendency_of_sea_water_salinity_expressed_as_salt_content',
          #                  'long_name'     : 'Tendency of Sea Water Salinity Expressed as Salt Content',
          #                  'units'         : 'g m-2 s-1',
          #                  'dimensions'    : 2,
          #                  'stagger'       : 'c',
          #                  'coordinates'   : 'lat lon',
          #                },
          #'SFORC_S'     : { 'esgf_name'     : 'ssltff',
          #                  'standard_name' : 'surface_forcing_salinity_flux',
          #                  'long_name'     : 'Surface Forcing Salinity Flux',
          #                  'units'         : 'g m-2 s-1',
          #                  'dimensions'    : 2,
          #                  'stagger'       : 'c',
          #                  'coordinates'   : 'lat lon',
          #                },
          #'SFORC_T'     : { 'esgf_name'     : 'sthff',
          #                  'standard_name' : 'surface_forcing_energy_flux',
          #                  'long_name'     : 'Surface Forcing Temperature Flux',
          #                  'units'         : 'W m-2',
          #                  'dimensions'    : 2,
          #                  'stagger'       : 'c',
          #                  'coordinates'   : 'lat lon',
          #                },
          'SWAVE'       : { 'esgf_name'     : 'rsdo',
                            'standard_name' : 'surface_net_shortwave_radiation_flux',
                            'long_name'     : 'Surface Net Shortwave Flux',
                            'units'         : 'W m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'T_SFLUX'     : { 'esgf_name'     : 'stsltf',
                            'standard_name' : 'surface_total_salinity_flux',
                            'long_name'     : 'Surface Total Salinity Flux',
                            'units'         : 'g m-2 s-1',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'T_TFLUX'     : { 'esgf_name'     : 'thltf',
                            'standard_name' : 'surface_total_theta_flux',
                            'long_name'     : 'Surface Total Theta Flux',
                            'units'         : 'degC s-1',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'USLTMASS'    : { 'esgf_name'     : 'usltmo',
                            'standard_name' : 'zonal_mass-weight_salinity_transport',
                            'long_name'     : 'Zonal Mass-weight Salinity Transport',
                            'units'         : 'g kg-1 m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'VSLTMASS'    : { 'esgf_name'     : 'vsltmo',
                            'standard_name' : 'meridional_mass-weight_salinity_transport',
                            'long_name'     : 'Meridional Mass-weight Salinity Transport',
                            'units'         : 'g kg-1 m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'UTHMASS'     : { 'esgf_name'     : 'uthmo',
                            'standard_name' : 'zonal_mass-weight_potential_temperature_transport',
                            'long_name'     : 'Zonal Mass-weight Potntial Temperature Transport',
                            'units'         : 'degree_C m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'VTHMASS'     : { 'esgf_name'     : 'vthmo',
                            'standard_name' : 'meridional_mass-weight_potential_temperature_transport',
                            'long_name'     : 'Meridional Mass-weight Potntial Temperature Transport',
                            'units'         : 'degree_C m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'UVEL'        : { 'esgf_name'     : 'uo',
                            'standard_name' : 'zonal_component_of_water_velocity',
                            'long_name'     : 'Zonal Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'VVEL'        : { 'esgf_name'     : 'vo',
                            'standard_name' : 'meridional_component_of_water_velocity',
                            'long_name'     : 'Meridional Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          'WVEL'        : { 'esgf_name'     : 'wo',
                            'standard_name' : 'vertical_component_of_water_velocity',
                            'long_name'     : 'Vertical Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'z',
                            'coordinates'   : 'lat lon',
                          },
          'UVELMASS'    : { 'esgf_name'     : 'umo',
                            'standard_name' : 'zonal_mass-weighted_component_of_water_velocity',
                            'long_name'     : 'Zonal Mass Weighted Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'VVELMASS'    : { 'esgf_name'     : 'vmo',
                            'standard_name' : 'meridional_mass-weighted_component_of_water_velocity',
                            'long_name'     : 'Meridional Mass Weighted Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          'U_WSTRESS'   : { 'esgf_name'     : 'tauu',
                            'standard_name' : 'surface_zonal_wind_stress',
                            'long_name'     : 'Surface Zonal Wind Stress',
                            'units'         : 'N m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'V_WSTRESS'   : { 'esgf_name'     : 'tauv',
                            'standard_name' : 'surface_meridional_wind_stress',
                            'long_name'     : 'Surface Meridional Wind Stress',
                            'units'         : 'N m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          #'pickup'      : { 'esgf_name'     : 'pickup',
          #                  'standard_name' : 'pickup',
          #                  'long_name'     : 'Pickup field',
          #                  'units'         : '1',
          #                  'dimensions'    : NFPICKUP,
          #                  'stagger'       : 'none',
          #                  'coordinates'   : 'lat lon',
          #                },
          #'pickup_ggl90': { 'esgf_name'     : 'pickup_ggl90',
          #                  'standard_name' : 'pickup_ggl90',
          #                  'long_name'     : 'Pickup field for ggl90',
          #                  'units'         : '1',
          #                  'dimensions'    : 3,
          #                  'stagger'       : 'none',
          #                  'coordinates'   : 'lat lon',
          #                },
          }

mask = np.fromfile('hFacC.data','>f4').reshape((1,NZ,NY,NX)) > 0.0

for binfile in sys.argv[1:]:
    name = os.path.basename(os.path.splitext(binfile)[0])

    try:
        vname,vdate = name.split('.')
    except:
        continue

    if vname not in names.keys( ):
        continue

    stime = float(vdate)*timestep
    e_ym = (datetime.datetime.fromisoformat(start_simulation)+
            datetime.timedelta(seconds=stime))
    s_ym = e_ym + dateutil.relativedelta.relativedelta(months=-1)

    print(vname,s_ym)

    if names[vname]['stagger'] == 'c':
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 20
      nnx2 = 631
      nny1 = 1
      nny2 = 362
    elif names[vname]['stagger'] == 'u':
      lonfile = 'XG.data'
      latfile = 'YC.data'
      nnx1 = 20
      nnx2 = 631
      nny1 = 1
      nny2 = 362
    elif names[vname]['stagger'] == 'v':
      lonfile = 'XC.data'
      latfile = 'YG.data'
      nnx1 = 20
      nnx2 = 631
      nny1 = 1
      nny2 = 362
    elif names[vname]['stagger'] == 'z':
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 20
      nnx2 = 631
      nny1 = 1
      nny2 = 362
    else:
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 0
      nnx2 = NX
      nny1 = 0
      nny2 = NY

    lon = np.fromfile(lonfile, '>f4').reshape((NY,NX))
    lat = np.fromfile(latfile, '>f4').reshape((NY,NX))

    xlon = xr.DataArray(name = "lon",
                        data = lon[nny1:nny2,nnx1:nnx2],
                        dims = ["lat","lon"],
                        attrs = dict(standard_name = "longitude",
                                     units = "degrees_east"))
    xlat = xr.DataArray(name = "lat",
                        data = lat[nny1:nny2,nnx1:nnx2],
                        dims = ["lat","lon"],
                        attrs = dict(standard_name = "latitude",
                                     units = "degrees_north"))
    xbnds = xr.DataArray(name = "depth_bnds",
                         data = zz,
                         dims = ["depth","bnds"],
                         attrs = dict(standard_name = "depth_bounds",
                                      units = "m"))
    xdepth = xr.DataArray(name = "depth",
                          data = zc, 
                          dims = ["depth"],
                          attrs = dict(standard_name = "depth",
                                       bounds = "depth_bnds",
                                       units = "m"))
    xfield = xr.DataArray(name = "field",
                          data = np.linspace(1,NFPICKUP,NFPICKUP), 
                          dims = ["field"],
                          attrs = dict(standard_name = "field",
                                       units = "1"))
    xtime = xr.DataArray(name = "time",
                         data = np.array((stime,)),
                         dims = ["time"],
                         attrs = dict(standard_name = "time",
                                      calendar = calendar,
                                      units = "seconds since "+
                                      start_simulation+' UTC'))
    if names[vname]['dimensions'] == 2:
        dims = ["time","lat","lon"]
        coords = dict(lon = xlon, lat = xlat, time = xtime)
        count = NY*NX
        rv = np.fromfile(binfile, '>f4', count = count).reshape(1,NY,NX)
        h = np.where(mask[0,0,:,:],rv,np.nan)
    elif names[vname]['dimensions'] == 3:
        coords = dict(lon = xlon, lat = xlat, depth = xdepth, time = xtime)
        count = NZ*NY*NX
        if 'pickup' in vname:
            dims = ["time","field","lat","lon"]
            h = np.fromfile(binfile, '>f8',
                        count = count).reshape(1,NZ,NY,NX)
        else:
            dims = ["time","depth","lat","lon"]
            rv = np.fromfile(binfile, '>f4',
                        count = count).reshape(1,NZ,NY,NX)
            h = np.where(mask,rv,np.nan)
    else:
        if vname == 'pickup':
            dims = ["time","field","lon","lat"]
            coords = dict(lon = xlon, lat = xlat, field = xfield, time = xtime)
            count = NFPICKUP*NY*NX
            h = np.fromfile(binfile, '>f8',
                        count = count).reshape(1,NFPICKUP,NY,NX)
        else:
            print('Unrecognized number of dimensions for ',vname)
            continue
    try:
        infname = names[vname]['esgf_name']
    except:
        infname = vname

    da = xr.DataArray(name = infname, data = h[Ellipsis,nny1:nny2,nnx1:nnx2],
                      dims = dims, coords = coords,
                      attrs = dict(standard_name = names[vname]['standard_name'],
                                   long_name = names[vname]['long_name'],
                                   units = names[vname]['units'],
                                   coordinates = names[vname]['coordinates']),
                     )
    ds = da.to_dataset( )
    if names[vname]['dimensions'] == 3:
        ds["depth_bnds"] = xbnds
    now = datetime.datetime.now( ).isoformat( )
    ds.attrs['Conventions'] = "CF-1.11"
    ds.attrs['creation_date'] = now
    ds.attrs['tracking_id'] = 'hdl:21.14103/'+str(uuid.uuid1( ))
    ds.attrs['description'] = domain+' simulation'
    ds.attrs['title'] = 'Coupled RegCM-ES1-1 simulation. Ocean Component is MITgcm checkpoint69e. Output prepared for CORDEX experiment'
    ds.attrs['activity_id'] = 'CORDEX'
    ds.attrs['contact'] = 'ggiulian@ictp.it'
    ds.attrs['experiment_id'] = experiment
    ds.attrs['domain'] = 'Mediterranean'
    ds.attrs['domain_id'] = domain
    ds.attrs['grid'] = 'NEMO ORCA tripolar resolution 1/12 deg'
    if experiment == 'evaluation':
        ds.attrs['driving_experiment'] = 'reanalysis simulation of the recent past'
    elif experiment == 'historical':
        ds.attrs['driving_experiment'] = 'scenario simulation of the recent past'
    else:
        ds.attrs['driving_experiment'] = 'future scenario simulation'
    ds.attrs['driving_experiment_id'] = experiment
    ds.attrs['driving_institution_id'] = ginst
    ds.attrs['driving_source_id'] = gmodel
    ds.attrs['driving_variant_label'] = gmemb
    ds.attrs['institution'] = 'The Abdus Salam International Centre for Theoretical Physics, Trieste, Italy'
    ds.attrs['institution_id'] = myinst
    ds.attrs['license'] = 'https://cordex.org/data-access/cordex-cmip6-data/cordex-cmip6-terms-of-use'
    ds.attrs['mip_era'] = 'CMIP6'
    ds.attrs['product'] = 'model-output'
    ds.attrs['project_id'] = 'CORDEX-CMIP6'
    ds.attrs['source'] = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5.0, MITgcm v6.9d and CHyM (2025)'
    ds.attrs['source_id'] = 'RegCM-ES1-1'
    ds.attrs['source_type'] = 'AORCM'
    ds.attrs['realm'] = 'ocean'
    ds.attrs['table_id'] = 'Table mon'
    ds.attrs['frequency'] = 'mon'
    ds.attrs['variable_id'] = infname
    ds.attrs['version_realization'] = 'v1-r1'
    ds.attrs['version_realization_info'] = 'none'
    ds.attrs['activity_participation'] = 'DD'
    ds.attrs['cohort'] = 'Registered'
    ds.attrs['further_info_url'] = 'https://www.medcordex.eu/Med-CORDEX-2_baseline-runs_protocol.pdf'
    ds.attrs['label'] = 'RegCM-ES1-1'
    ds.attrs['label_extended'] = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5.0, MITgcm v6.9d and CHyM (2025)'
    ds.attrs['release_year'] = '2025'
    ds.attrs['title'] = 'ICTP Regional Climatic Coupled model V1.1'
    ds.attrs['references'] = 'https://github.com/graziano-giuliani/MED12-ocean-mit'
    ds.attrs['model_revision'] = '1.1'
    ds.attrs['history'] = now+': Created by RegCM-ES model run'
    if vname == 'pickup':
        ds.attrs['FieldList'] = pickup_flds

    for ff in ['data', 'data.pkg', 'data.cal', 'data.ggl90',
               'data.rbcs', 'data.obcs']:
        att1 = f90nml.read(ff)
        if ff == "data":
            aa = "mit"
        else:
            aa = os.path.splitext(ff)[1][1:]
        for v in att1.keys( ):
            for a in att1[v].keys( ):
                ds.attrs[aa+'_'+a] = str(att1[v][a])

    opath = os.path.join(outpath,'CORDEX-CMIP6','DD',domain,myinst,
            gmodel,experiment,gmemb,'RegCM-ES1-1','v1-r1','mon',
            infname)
    os.makedirs(opath,exist_ok=True)
    ncfile = os.path.join(opath, infname + '_' + domain + '_' + gmodel +
            '_' + experiment + '_' + gmemb + '_' + myinst +
            '_RegCM-ES1-1_v1-r1_mon_' + s_ym.strftime('%Y%m') + '-' +
            e_ym.strftime('%Y%m') + '.nc')
    encode = { infname : { 'zlib': True,
                           'complevel' : 6,
                           'significant_digits' : 4,
                         },
             }
    try:
        ds.to_netcdf(ncfile, format = 'NETCDF4', encoding = encode,
                unlimited_dims = ('time'))
    except:
        print('Error for ',ncfile)
        continue
    metafile = os.path.splitext(binfile)[0]+'.meta'
    try:
        os.unlink(binfile)
        os.unlink(metafile)
    except:
        pass

