#!/usr/bin/env python3

import os
import sys
import datetime
import dateutil
import uuid
import numpy as np
import xarray as xr
import f90nml

# Need to be setup.
NX = 660
NY = 368
NZ = 75
NFPICKUP = 453
timestep = 150
start_simulation = "1979-08-01 00:00:00"
domain = 'MED-12'
myinst = 'ICTP'
ginst = 'ECMWF'
gmodel = 'ERA5'
gmemb = 'r1i1p1f1'
experiment = 'evaluation'
outpath = '.'
# End Setup

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
          'EmPmR'       : { 'esgf_name'     : 'sltnf',
                            'standard_name' : 'net_freshwater_flux',
                            'long_name'     : 'Net freshwater flux into the ocean',
                            'units'         : 'm/s',
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
                            'long_name'     : 'Ocean Mixed Layer Thicknes',
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
          #'pickup'      : { 'standard_name' : 'pickup',
          #                  'long_name'     : 'Pickup field',
          #                  'units'         : '1',
          #                  'dimensions'    : NFPICKUP,
          #                  'coordinates'   : 'lat lon',
          #                },
          #'pickup_ggl90': { 'standard_name' : 'pickup_ggl90',
          #                  'long_name'     : 'Pickup field for ggl90',
          #                  'units'         : '1',
          #                  'dimensions'    : 3,
          #                  'coordinates'   : 'lat lon',
          #                },
          }

depth = np.array((0.525366611563235, 1.63218471391611, 2.85905740165649, 
    4.22284435423749, 5.74273041043513, 7.44053341546443, 9.34104895575542, 
    11.472435216752, 13.8666410979201, 16.5598804577976, 19.5931548848141, 
    23.0128266283666, 26.8712421967803, 31.2274055372057, 36.1476975462358, 
    41.706635797057, 47.9876646822709, 55.0839615396682, 63.0992386518988, 
    72.1485142374656, 82.3588177073313, 93.8697857000613, 106.834096056691, 
    121.417677516769, 137.79962436194, 156.171738686131, 176.737619951045, 
    199.71122379278, 225.31482162003, 253.776311213825, 285.325857647152, 
    320.191883783609, 358.596479331253, 400.750353996665, 446.847518727332, 
    497.059932526908, 551.532392928262, 610.377968057859, 673.67426112225, 
    741.46076112225, 813.737468057859, 890.464892928262, 971.565432526908, 
    1056.92601872733, 1146.40185399667, 1239.82097933125, 1336.98938378361, 
    1437.69635764715, 1541.71981121382, 1648.83132162003, 1758.80072379278, 
    1871.40011995104, 1986.40723868613, 2103.60812436194, 2222.79917751677, 
    2343.78859605669, 2466.39728570006, 2590.45931770733, 2715.82201423747, 
    2842.3457386519, 2969.90346153967, 3098.38016468227, 3227.67213579706, 
    3357.68619754624, 3488.33890553721, 3619.55574219678, 3751.27032662837, 
    3883.42365488481, 4015.9633804578, 4148.84314109792, 4282.02193521675, 
    4415.46354895576, 4549.13603341546, 4683.01123041044, 4817.06434435424))

depthl = np.array((1.05073322, 2.21363620, 3.50447860, 4.94121011,
                   6.54425071, 8.33681612, 10.3452818, 12.5995886,
                   15.1336936, 17.9860674, 21.2002424, 24.8254108,
                   28.9170735, 33.5377375, 38.7576576, 44.6556140,
                   51.3197153, 58.8482077, 67.3502696, 76.9467589,
                   87.7708765, 99.9686949, 113.699497, 129.135858,
                   146.463391, 165.880086, 187.595153, 211.827294,
                   238.802349, 268.750273, 301.901442, 338.482326,
                   378.710633, 422.790075, 470.904963, 523.214903,
                   579.849883, 640.906053, 706.442469, 776.479053,
                   850.995883, 929.933903, 1013.19696, 1100.65507,
                   1192.14863, 1287.49333, 1386.48544, 1488.90727,
                   1594.53235, 1703.13029, 1814.47115, 1928.32909,
                   2044.48539, 2162.73086, 2282.86750, 2404.70969,
                   2528.08488, 2652.83376, 2778.81027, 2905.88121,
                   3033.92572, 3162.83461, 3292.50966, 3422.86274,
                   3553.81507, 3685.29641, 3817.24424, 3949.60307,
                   4082.32369, 4215.36259, 4348.68128, 4482.24582,
                   4616.02625, 4749.99621, 4884.13248))


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
      lonfile = 'LONC.bin'
      latfile = 'LATC.bin'
      zc = depth
    elif names[vname]['stagger'] == 'u':
      lonfile = 'LONG.bin'
      latfile = 'LATC.bin'
      zc = depth
    elif names[vname]['stagger'] == 'v':
      lonfile = 'LONG.bin'
      latfile = 'LATC.bin'
      zc = depth
    elif names[vname]['stagger'] == 'z':
      lonfile = 'LONC.bin'
      latfile = 'LATC.bin'
      zc = depthl

    lon = np.fromfile(lonfile, '>f4').reshape(NY,NX)
    lat = np.fromfile(latfile, '>f4').reshape(NY,NX)

    xlon = xr.DataArray(name = "lon",
                        data = lon, 
                        dims = ["lon","lat"],
                        attrs = dict(standard_name = "longitude",
                                     units = "degrees_east"))
    xlat = xr.DataArray(name = "lat",
                        data = lat, 
                        dims = ["lon","lat"],
                        attrs = dict(standard_name = "latitude",
                                     units = "degrees_north"))
    xdepth = xr.DataArray(name = "depth",
                          data = zc, 
                          dims = ["depth"],
                          attrs = dict(standard_name = "depth",
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
                                      units = "seconds since "+
                                      start_simulation+' UTC'))

    if names[vname]['dimensions'] == 3:
        dims = ["time","depth","lon","lat"]
        coords = dict(lon = xlon, lat = xlat, depth = xdepth, time = xtime)
        count = NZ*NY*NX
        if 'pickup' in vname:
            h = np.fromfile(binfile, '>f8',
                        count = count).reshape(1,NZ,NY,NX)
        else:
            h = np.fromfile(binfile, '>f4',
                        count = count).reshape(1,NZ,NY,NX)
    elif names[vname]['dimensions'] == NFPICKUP:
        dims = ["time","field","lon","lat"]
        coords = dict(lon = xlon, lat = xlat, field = xfield, time = xtime)
        count = NFPICKUP*NY*NX
        h = np.fromfile(binfile, '>f8',
                    count = count).reshape(1,NFPICKUP,NY,NX)
    else:
        dims = ["time","lon","lat"]
        coords = dict(lon = xlon, lat = xlat, time = xtime)
        count = NY*NX
        h = np.fromfile(binfile, '>f4',
                    count = count).reshape(1,NY,NX)
    try:
        infname = names[vname]['esgf_name']
    except:
        infname = vname
    da = xr.DataArray(name = infname, data=h, dims = dims, coords = coords,
                      attrs = dict(standard_name = names[vname]['standard_name'],
                                   long_name = names[vname]['long_name'],
                                   units = names[vname]['units'],
                                   coordinates = names[vname]['coordinates']),
                     )
    ds = da.to_dataset( )
    now = datetime.datetime.now( ).isoformat( )
    ds.attrs['Conventions'] = "CF-1.9"
    ds.attrs['creation_date'] = now
    ds.attrs['tracking_id'] = str(uuid.uuid1( ))
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
    ds.attrs['institution'] = 'International Centre for Theoretical Physics'
    ds.attrs['institution_id'] = myinst
    ds.attrs['license'] = 'Creative Commons Attribution 4.0 International License (CC BY 4.0; https://creativecommons.org/licenses/by/4.0).'
    ds.attrs['mip_era'] = 'CMIP6'
    ds.attrs['product'] = 'model-output'
    ds.attrs['project_id'] = 'CORDEX'
    ds.attrs['source'] = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5, MITgcm v69 and CHyM'
    ds.attrs['source_id'] = 'RegCM-ES1-1'
    ds.attrs['source_type'] = 'AORCM'
    ds.attrs['realm'] = 'ocean'
    ds.attrs['table_id'] = 'Omon'
    ds.attrs['frequency'] = 'mon'
    ds.attrs['variable_id'] = infname
    ds.attrs['version_realization'] = 'v1-r1'
    ds.attrs['version_realization_info'] = 'none'
    ds.attrs['activity_participation'] = 'DD'
    ds.attrs['cohort'] = 'Registered'
    ds.attrs['further_info_url'] = 'https://www.medcordex.eu/Med-CORDEX-2_baseline-runs_protocol.pdf'
    ds.attrs['label'] = 'RegCM-ES1-1'
    ds.attrs['label_extended'] = 'The Regional Earth System Model RegCM-ES version 1.1 based on RegCM v5, MITgcm v69 and CHyM'
    ds.attrs['release_year'] = '2025'
    ds.attrs['title'] = 'ICTP Regional Climatic Coupled model V1.1'
    ds.attrs['references'] = 'https://github.com/graziano-giuliani/MED12-ocean-mit'
    ds.attrs['model_revision'] = '1.1'
    ds.attrs['history'] = now+': Created by RegCM-ES model run'

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
            '_RegCM-ES1-1_v1-r1_' + s_ym.strftime('%Y%m') + '-' +
            e_ym.strftime('%Y%m') + '.nc')
    encode = { infname : { 'zlib': True,
                           'complevel' : 6,
                           'significant_digits' : 4,
                         }
             }
    try:
        ds.to_netcdf(ncfile, format = 'NETCDF4', encoding = encode)
    except:
        print('Error for ',ncfile)
        continue
    metafile = os.path.splitext(binfile)[0]+'.meta'
    try:
        os.unlink(binfile)
        os.unlink(metafile)
    except:
        pass

