#!/usr/bin/env python3

import os
import sys
import numpy as np
import xarray as xr

# Need to be setup.
NX = 660
NY = 368
NZ = 75
NFPICKUP = 453
timestep = 150
start_simulation = "1979-08-01 00:00:00 UTC"

names = { 'SALT'        : { 'standard_name' : 'sea_water_absolute_salinity',
                            'long_name'     : 'Ocean salinity',
                            'units'         : 'g kg-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'THETA'       : { 'standard_name' : 'sea_water_potential_temperature',
                            'long_name'     : 'Ocean potential temperature',
                            'units'         : 'degree_C',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'RHO'         : { 'standard_name' : 'sea_water_density_anomaly',
                            'long_name'     : 'Density anomaly',
                            'units'         : 'kg m-3',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'ELEVATION'   : { 'standard_name' : 'sea_surface_elevation_anomaly',
                            'long_name'     : 'Sea Surface Elevation Anomaly',
                            'units'         : 'm',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'HFLUX'       : { 'standard_name' : 'net_heat_flux',
                            'long_name'     : 'Net Heat Flux',
                            'units'         : 'W m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EmPmR'       : { 'standard_name' : 'net_upward_freshwater_flux',
                            'long_name'     : 'Net upward freshwater flux',
                            'units'         : 'm/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFempmr'    : { 'standard_name' : 'net_upward_freshwater_flux',
                            'long_name'     : 'Forcing Net upward freshwater flux',
                            'units'         : 'm/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'EXFroff'     : { 'standard_name' : 'river_freshwater_flux',
                            'long_name'     : 'Forcing River freshwater flux',
                            'units'         : 'm/s',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'MLD'         : { 'standard_name' : 'depth_of_mixed_layer',
                            'long_name'     : 'Mixed Layer Depth',
                            'units'         : 'm',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'SFLUX'       : { 'standard_name' : 'surface_net_salinity_flux',
                            'long_name'     : 'Surface Net Salinity Flux',
                            'units'         : 'g m-2 s-1',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'SFORC_S'     : { 'standard_name' : 'surface_forcing_salinity_flux',
                            'long_name'     : 'Surface Forcing Salinity Flux',
                            'units'         : 'g m-2 s-1',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'SFORC_T'     : { 'standard_name' : 'surface_forcing_energy_flux',
                            'long_name'     : 'Surface Forcing Temperature Flux',
                            'units'         : 'W m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'SWAVE'       : { 'standard_name' : 'surface_net_shortwave_radiation_flux',
                            'long_name'     : 'Surface Net Shortwave Flux',
                            'units'         : 'W m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'T_SFLUX'     : { 'standard_name' : 'surface_total_salinity_flux',
                            'long_name'     : 'Surface Total Salinity Flux',
                            'units'         : 'g m-2 s-1',
                            'dimensions'    : 2,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'USLTMASS'    : { 'standard_name' : 'zonal_mass-weight_salinity_transport',
                            'long_name'     : 'Zonal Mass-weight Salinity Transport',
                            'units'         : 'g kg-1 m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'VSLTMASS'    : { 'standard_name' : 'meridional_mass-weight_salinity_transport',
                            'long_name'     : 'Meridional Mass-weight Salinity Transport',
                            'units'         : 'g kg-1 m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'UTHMASS'     : { 'standard_name' : 'zonal_mass-weight_potential_temperature_transport',
                            'long_name'     : 'Zonal Mass-weight Potntial Temperature Transport',
                            'units'         : 'degree_C m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'VTHMASS'     : { 'standard_name' : 'meridional_mass-weight_potential_temperature_transport',
                            'long_name'     : 'Meridional Mass-weight Potntial Temperature Transport',
                            'units'         : 'degree_C m s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'c',
                            'coordinates'   : 'lat lon',
                          },
          'UVEL'        : { 'standard_name' : 'zonal_component_of_water_velocity',
                            'long_name'     : 'Zonal Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'VVEL'        : { 'standard_name' : 'meridional_component_of_water_velocity',
                            'long_name'     : 'Meridional Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          'WVEL'        : { 'standard_name' : 'vertical_component_of_water_velocity',
                            'long_name'     : 'Vertical Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'z',
                            'coordinates'   : 'lat lon',
                          },
          'UVELMASS'    : { 'standard_name' : 'zonal_mass-weighted_component_of_water_velocity',
                            'long_name'     : 'Zonal Mass Weighted Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'VVELMASS'    : { 'standard_name' : 'meridional_mass-weighted_component_of_water_velocity',
                            'long_name'     : 'Meridional Mass Weighted Water Velocity',
                            'units'         : 'm s-1',
                            'dimensions'    : 3,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          'U_WSTRESS'   : { 'standard_name' : 'surface_zonal_wind_stress',
                            'long_name'     : 'Surface Zonal Wind Stress',
                            'units'         : 'N m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'u',
                            'coordinates'   : 'lat lon',
                          },
          'V_WSTRESS'   : { 'standard_name' : 'surface_meridional_wind_stress',
                            'long_name'     : 'Surface Meridional Wind Stress',
                            'units'         : 'N m-2',
                            'dimensions'    : 2,
                            'stagger'       : 'v',
                            'coordinates'   : 'lat lon',
                          },
          'pickup'      : { 'standard_name' : 'pickup',
                            'long_name'     : 'Pickup field',
                            'units'         : '1',
                            'dimensions'    : NFPICKUP,
                            'coordinates'   : 'lat lon',
                          },
          'pickup_ggl90': { 'standard_name' : 'pickup_ggl90',
                            'long_name'     : 'Pickup field for ggl90',
                            'units'         : '1',
                            'dimensions'    : 3,
                            'coordinates'   : 'lat lon',
                          },
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
    ncfile = name + '.nc'
    vname,vdate = name.split('.')

    time = float(vdate)*timestep

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
                         data = np.array((time,)),
                         dims = ["time"],
                         attrs = dict(standard_name = "time",
                                      units = "seconds since "+start_simulation))

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
    da = xr.DataArray(name = vname, data=h, dims = dims, coords = coords,
                      attrs = dict(standard_name = names[vname]['standard_name'],
                                   long_name = names[vname]['long_name'],
                                   units = names[vname]['units'],
                                   coordinates = names[vname]['coordinates']),
                     )
    da.to_netcdf(ncfile)
