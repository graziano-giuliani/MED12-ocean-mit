#!/usr/bin/env python3

"""
mitgcmtonc.py — Convert MITgcm binary output to CORDEX-CMIP6 NetCDF4.

Usage:
    mitgcmtonc.py <binfile> [<binfile> ...]

Each <binfile> must be a MITgcm diagnostic output file named as
<VARNAME>.<ITER>.data (e.g. THETA.0000043200.data).  The script reads
the matching .meta file implicitly via MITgcmutils.mds.

Required files in the working directory:
    hFacC.data / hFacC.meta   land/sea mask and grid dimensions
    XC.data, YC.data          tracer (C-grid) lon/lat
    XG.data, YG.data          u/v-point (G-grid) lon/lat
    RC.data                   cell-centre depths (negative, m)
    RF.data                   cell-face depths  (negative, m)
    data, data.pkg, ...       f90 namelist files (written to NC global attrs)

Output is written to:
    <outpath>/CORDEX-CMIP6/DD/<domain>/<inst>/<driver>/<experiment>/
    <member>/<source_id>/<version>/<freq>/<variable>/
    <variable>_<domain>_..._<freq>_<start>-<end>.nc

Dependencies:
    numpy, xarray, MITgcmutils, f90nml, python-dateutil
"""

import os
import sys
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import glob
import uuid
import numpy as np
import shutil
import xarray as xr
from MITgcmutils import mds
from netCDF4 import Dataset
import f90nml

# ---- USER CONFIGURATION ------------------------------------------------
timestep = 150            # MITgcm timestep in seconds (deltaT in data namelist)
start_simulation = "1979-08-01 00:00:00"  # simulation t=0 (ISO 8601)
calendar = "proleptic_gregorian" # CF calendar name;
                          # pure Gregorian without Julian cutover
domain = 'MED-12'         # CORDEX domain_id
myinst = 'ICTP'           # institution_id
ginst  = 'ECMWF'          # driving_institution_id
gmodel = 'ERA5'           # driving_source_id
gmemb  = 'r1i1p1f1'       # driving_variant_label
experiment = 'evaluation' # CORDEX experiment_id
outpath = '.'             # root output directory
maxx2 = 631
maxy2 = 362
regular_ll_grid = False
nemo_grid = '/leonardo/home/userexternal/ggiulian/project/MITGCM/MED12-ocean-mit/grid/1_coordinates_ORCA_R12.nc'
# ---- END CONFIGURATION -------------------------------------------------

def getcoordbounds(fname,which,i1,i2,j1,j2):
    if (which == 'c' or which == 'z'):
        with Dataset(fname) as mesh:
            glam = mesh.variables['glamf'][0]
            gphi =  mesh.variables['gphif'][0]
    elif which == 'u':
        with Dataset(fname) as mesh:
            glam = mesh.variables['glamv'][0]
            gphi =  mesh.variables['gphiv'][0]
    elif which == 'v':
        with Dataset(fname) as mesh:
            glam = mesh.variables['glamu'][0]
            gphi =  mesh.variables['gphiu'][0]
    else:
        return None
    lon_corners = np.stack([
          np.roll(np.roll(glam, 1, axis=0), 1, axis=1),  # SW: glam[j-1, i-1]
          np.roll(glam, 1, axis=0),                      # SE: glam[j-1, i]
          glam,                                          # NE: glam[j, i]
          np.roll(glam, 1, axis=1),                      # NW: glam[j, i-1]
        ], axis=-1)
    lat_corners = np.stack([
          np.roll(np.roll(gphi, 1, axis=0), 1, axis=1),
          np.roll(gphi, 1, axis=0),
          gphi,
          np.roll(gphi, 1, axis=1),
        ], axis=-1)
    return(lon_corners[j1:j2,i1:i2,:],lat_corners[j1:j2,i1:i2,:])

table_map = {'mon': 'Omon',
             'day': 'Oday'}

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

# Variable mapping: MITgcm internal name -> CORDEX-CMIP6 metadata.
# Keys:  esgf_name     short variable name as published on ESGF
#        standard_name CF standard name (must match CF table exactly)
#        long_name     human-readable description
#        units         CF unit string (space-separated, negative exponents)
#        dimensions    2 = surface field, 3 = full 3-D field
#        stagger       'c'=tracer, 'u'=zonal, 'v'=meridional, 'z'=vertical
#        coordinates   auxiliary coordinate variables to attach
names = {
          'EXFtaux'     : { 'esgf_name'     : 'ftaux',
     'standard_name' : 'downward_x_stress_at_sea_water_surface',
     'long_name'     : 'X Component of Wind Stress at Sea Surface',
     'units'         : 'Pa',
     'notes'         : 'U Ocean velocity increase if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFtauy'     : { 'esgf_name'     : 'ftauy',
     'standard_name' : 'downward_y_stress_at_sea_water_surface',
     'long_name'     : 'Y Component of Wind Stress at Sea Surface',
     'units'         : 'Pa',
     'notes'         : 'V Ocean velocity increase if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFevap'     : { 'esgf_name'     : 'fevap',
     'standard_name' : 'evaporation_flux_at_sea_water_surface',
     'long_name'     : 'Evaporation flux at Sea Surface',
     'units'         : 'm s-1',
     'notes'         : 'Ocean salinity increases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFpreci'    : { 'esgf_name'     : 'fpr',
     'standard_name' : 'precipitation_flux_at_sea_water_surface',
     'long_name'     : 'Precipitation flux at Sea Surface',
     'units'         : 'm s-1',
     'notes'         : 'Ocean salinity decreases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFhl'       : { 'esgf_name'     : 'fhfls',
     'standard_name' : 'downward_latent_heat_flux_at_sea_water_surface',
     'long_name'     : 'Latent heat flux at Sea Surface',
     'units'         : 'W/m2',
     'notes'         : 'Ocean temperature increases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFhs'       : { 'esgf_name'     : 'fhfss',
     'standard_name' : 'downward_sensible_heat_flux_at_sea_water_surface',
     'long_name'     : 'Sensible heat flux at Sea Surface',
     'units'         : 'W/m2',
     'notes'         : 'Ocean temperature increases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFlwnet'    : { 'esgf_name'     : 'frlntus',
     'standard_name' : 'net_upward_longwave_flux_at_sea_water_surface',
     'long_name'     : 'Net Upward Longwave Radiation at Sea Water Surface',
     'units'         : 'W m-2',
     'notes'         : 'Ocean temperature decreases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFswnet'    : { 'esgf_name'     : 'frsntus',
     'standard_name' : 'net_upward_shortwave_flux_at_sea_water_surface',
     'long_name'     : 'Net Upward Shortwave Radiation at Sea Water Surface',
     'units'         : 'W m-2',
     'notes'         : 'Ocean temperature increases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'EXFroff'     : { 'esgf_name'     : 'friver',
     'standard_name' : 'water_flux_into_sea_water_from_rivers',
     'long_name'     : 'Forcing River freshwater flux',
     'units'         : 'm s-1',
     'notes'         : 'Ocean salinity decreases if positive',
     'comment'       : 'EXF package input to MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'SALT'        : { 'esgf_name'     : 'so',
     'standard_name' : 'sea_water_practical_salinity',
     'long_name'     : 'Ocean salinity',
     'units'         : '1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'THETA'       : { 'esgf_name'     : 'thetao',
     'standard_name' : 'sea_water_potential_temperature',
     'long_name'     : 'Ocean potential temperature',
     'units'         : 'degrees_Celsius',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'RHO'         : { 'esgf_name'     : 'rhopoto',
     'standard_name' : 'sea_water_potential_density_anomaly',
     'long_name'     : 'Sea Water Potential Density Anomaly',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'units'         : 'kg m-3',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'ELEVATION'   : { 'esgf_name'     : 'zos',
     'standard_name' : 'sea_surface_height_above_geoid',
     'long_name'     : 'Sea Surface Elevation Anomaly',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'units'         : 'm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'HFLUX'       : { 'esgf_name'     : 'hfndo',
     'standard_name' : 'surface_net_heat_flux_in_sea_water',
     'long_name'     : 'Net Heat Flux into the Ocean',
     'units'         : 'W m-2',
     'notes'         : 'Ocean temperature increases if positive',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'SWAVE'       : { 'esgf_name'     : 'rnsdo',
     'standard_name' : 'surface_net_shortwave_radiation_flux_in_sea_water',
     'long_name'     : 'Surface Net Shortwave Flux into the Ocean',
     'units'         : 'W m-2',
     'notes'         : 'Ocean temperature increases if positive',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'oceFWflx'    : { 'esgf_name'     : 'sltnf',
     'standard_name' : 'net_freshwater_flux',
     'long_name'     : 'Net Surface Freshwater Flux into the Ocean',
     'units'         : 'kg m-2 s-1',
     'notes'         : 'Ocean salinity decreases if positive',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'MLD'         : { 'esgf_name'     : 'mlot',
     'standard_name' : 'ocean_mixed_layer_thickness_defined_by_temperature',
     'long_name'     : 'Ocean Mixed Layer Thickness Definded by temperature',
     'units'         : 'm',
     'notes'         : 'The MITgcm model calculates the equivalent density drop corresponding to a 0.2C temperature drop using the thermal expansion coefficient',
     'comment'       : 'MITgcm Ocean output',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
#         'SFLUX'       : { 'esgf_name'     : 'osalttend',
#    'standard_name' : 'tendency_of_sea_water_salinity_expressed_as_salt_content',
#    'long_name'     : 'Tendency of Sea Water Salinity Expressed as Salt Content',
#    'units'         : 'g m-2 s-1',
#    'dimensions'    : 2,
#    'stagger'       : 'c',
#    'coordinates'   : 'lat lon',
#                         },
#         'SFORC_S'     : { 'esgf_name'     : 'ssltff',
#    'standard_name' : 'surface_forcing_salinity_flux',
#    'long_name'     : 'Surface Forcing Salinity Flux',
#    'units'         : 'g m-2 s-1',
#    'dimensions'    : 2,
#    'stagger'       : 'c',
#    'coordinates'   : 'lat lon',
#                         },
#         'SFORC_T'     : { 'esgf_name'     : 'sthff',
#    'standard_name' : 'surface_forcing_energy_flux',
#    'long_name'     : 'Surface Forcing Temperature Flux',
#    'units'         : 'W m-2',
#    'dimensions'    : 2,
#    'stagger'       : 'c',
#    'coordinates'   : 'lat lon',
#                         },
          'T_SFLUX'     : { 'esgf_name'     : 'tsltf',
     'standard_name' : 'total_salinity_flux',
     'long_name'     : 'Total Salinity Flux',
     'units'         : 'g m-2 s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'T_TFLUX'     : { 'esgf_name'     : 'thltf',
     'standard_name' : 'total_theta_flux',
     'long_name'     : 'Total Theta Flux',
     'units'         : 'degrees_Celsius s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'USLTMASS'    : { 'esgf_name'     : 'usltmo',
     'standard_name' : 'zonal_mass_weight_salinity_transport',
     'long_name'     : 'Zonal Mass-weight Salinity Transport',
     'units'         : 'g kg-1 m s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'VSLTMASS'    : { 'esgf_name'     : 'vsltmo',
     'standard_name' : 'meridional_mass-weight_salinity_transport',
     'long_name'     : 'Meridional Mass-weight Salinity Transport',
     'units'         : 'g kg-1 m s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'UTHMASS'     : { 'esgf_name'     : 'uthmo',
     'standard_name' : 'zonal_mass_weight_potential_temperature_transport',
     'long_name'     : 'Zonal Mass-weight Potntial Temperature Transport',
     'units'         : 'degrees_Celsius m s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'VTHMASS'     : { 'esgf_name'     : 'vthmo',
     'standard_name' : 'meridional_mass-weight_potential_temperature_transport',
     'long_name'     : 'Meridional Mass-weight Potntial Temperature Transport',
     'units'         : 'degrees_Celsius m s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'UVEL'        : { 'esgf_name'     : 'uo',
     'standard_name' : 'eastward_sea_water_velocity',
     'long_name'     : 'Eastward Sea Water Velocity',
     'units'         : 'm s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'u',
     'coordinates'   : 'lat lon',
                          },
          'VVEL'        : { 'esgf_name'     : 'vo',
     'standard_name' : 'northward_sea_water_velocity',
     'long_name'     : 'Northward Sea Water Velocity',
     'units'         : 'm s-1',
     'dimensions'    : 3,
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'stagger'       : 'v',
     'coordinates'   : 'lat lon',
                          },
          'WVEL'        : { 'esgf_name'     : 'wo',
     'standard_name' : 'upward_sea_water_velocity',
     'long_name'     : 'Upward Sea Water Velocity',
     'units'         : 'm s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'z',
     'coordinates'   : 'lat lon',
                          },
          'UVELMASS'    : { 'esgf_name'     : 'umo',
     'standard_name' : 'ocean_mass_x_transport',
     'long_name'     : 'Ocean Mass X Transport',
     'units'         : 'm s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'u',
     'coordinates'   : 'lat lon',
                          },
          'VVELMASS'    : { 'esgf_name'     : 'vmo',
     'standard_name' : 'ocean_mass_y_transport',
     'long_name'     : 'Ocean Mass Y transport',
     'units'         : 'm s-1',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 3,
     'stagger'       : 'v',
     'coordinates'   : 'lat lon',
                          },
          'U_WSTRESS'   : { 'esgf_name'     : 'tauuo',
     'standard_name' : 'surface_downward_x_stress',
     'long_name'     : 'Surface Downward X Stress',
     'units'         : 'N m-2',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'u',
     'coordinates'   : 'lat lon',
                          },
          'V_WSTRESS'   : { 'esgf_name'     : 'tauvo',
     'standard_name' : 'surface_downward_y_stress',
     'long_name'     : 'Surface Downward Y Stress',
     'units'         : 'N m-2',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'v',
     'coordinates'   : 'lat lon',
                          },
          'SST'      : { 'esgf_name'     : 'tos',
     'standard_name' : 'sea_surface_temperature',
     'long_name'     : 'Sea Surface Temperature',
     'units'         : 'degrees_Celsius',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
     'coordinates'   : 'lat lon',
                          },
          'SOS'      : { 'esgf_name'     : 'sos',
     'standard_name' : 'sea_surface_salinity',
     'long_name'     : 'Sea Surface Salinity',
     'units'         : '0.001',
     'notes'         : 'none',
     'comment'       : 'Output from MITgcm',
     'dimensions'    : 2,
     'stagger'       : 'c',
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

    etime = float(vdate)*timestep
    e_ym = (datetime.datetime.fromisoformat(start_simulation)+
            datetime.timedelta(seconds=etime))
    if vname in ['SST', 'SOS', 'ELEVATION']:
        s_ym = e_ym + relativedelta(days=-1)
        cfrq = 'day'
    else:
        s_ym = e_ym + relativedelta(months=-1)
        cfrq = 'mon'

    absolute_difference = e_ym - s_ym
    stime = etime - absolute_difference.total_seconds( )

    print(vname,s_ym)

    if names[vname]['stagger'] == 'c':
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 0
      nnx2 = maxx2
      nny1 = 0
      nny2 = maxy2
    elif names[vname]['stagger'] == 'u':
      lonfile = 'XG.data'
      latfile = 'YC.data'
      nnx1 = 0
      nnx2 = maxx2
      nny1 = 0
      nny2 = maxy2
    elif names[vname]['stagger'] == 'v':
      lonfile = 'XC.data'
      latfile = 'YG.data'
      nnx1 = 0
      nnx2 = maxx2
      nny1 = 0
      nny2 = maxy2
    elif names[vname]['stagger'] == 'z':
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 0
      nnx2 = maxx2
      nny1 = 0
      nny2 = maxy2
    else:
      lonfile = 'XC.data'
      latfile = 'YC.data'
      nnx1 = 0
      nnx2 = NX
      nny1 = 0
      nny2 = NY

    cbounds = None
    lon = np.fromfile(lonfile, '>f4').reshape((NY,NX))
    lat = np.fromfile(latfile, '>f4').reshape((NY,NX))
    if not regular_ll_grid:
        cbounds = getcoordbounds(nemo_grid,names[vname]['stagger'],
                                 nnx1,nnx2,nny1,nny2)

    if cbounds:
        xbnds = xr.DataArray(name = 'lon_bnds',
                             data = cbounds[0],
                             dims=['lat', 'lon', 'cbnds'],
                             attrs=dict(units='degrees_east')
                            )
        ybnds = xr.DataArray(name = 'lat_bnds',
                             data = cbounds[1],
                             dims=['lat', 'lon', 'cbnds'],
                             attrs=dict(units='degrees_north')
                            )
        xlon = xr.DataArray(name = "lon",
                            data = lon[nny1:nny2,nnx1:nnx2],
                            dims = ["lat","lon"],
                            attrs = dict(standard_name = "longitude",
                                         bounds = 'lon_bnds',
                                         units = "degrees_east"))
        xlat = xr.DataArray(name = "lat",
                            data = lat[nny1:nny2,nnx1:nnx2],
                            dims = ["lat","lon"],
                            attrs = dict(standard_name = "latitude",
                                         bounds = 'lat_bnds',
                                         units = "degrees_north"))
    else:   
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
    
    zbnds = xr.DataArray(name = "depth_bnds",
                         data = zz,
                         dims = ["depth","zbnds"],
                         attrs = dict(standard_name = "depth_bounds",
                                      units = "m"))
    xdepth = xr.DataArray(name = "depth",
                          data = zc, 
                          dims = ["depth"],
                          attrs = dict(standard_name = "depth",
                                       positive = "down",
                                       bounds = "depth_bnds",
                                       units = "m"))
    xfield = xr.DataArray(name = "field",
                          data = np.linspace(1,NFPICKUP,NFPICKUP), 
                          dims = ["field"],
                          attrs = dict(standard_name = "field",
                                       units = "1"))
    xtime_bnds = xr.DataArray(name="time_bnds",
                              data=np.array([[stime, etime]]),
                              dims=["time", "tbnds"],
                              attrs=dict(standard_name="time")
                             )
    xtime = xr.DataArray(name = "time",
                         data = np.array((etime,)),
                         dims = ["time"],
                         attrs = dict(standard_name = "time",
                                      calendar = calendar,
                                      bounds = "time_bnds",
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
            dims = ["time","depth","lat","lon"]
            h = np.fromfile(binfile, '>f8',
                            count = count).reshape(1,NZ,NY,NX)
        else:
            dims = ["time","depth","lat","lon"]
            rv = np.fromfile(binfile, '>f4',
                        count = count).reshape(1,NZ,NY,NX)
            h = np.where(mask,rv,np.nan)
    else:
        if vname == 'pickup':
            dims = ["time","field","lat","lon"]
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
                                   cell_methods = 'time_mean',
                                   comment = names[vname]['comment'],
                                   notes = names[vname]['notes'],
                                   long_name = names[vname]['long_name'],
                                   units = names[vname]['units'],
                                   coordinates = names[vname]['coordinates']),
                     )
    ds = da.to_dataset( )
    ds["time_bnds"] = xtime_bnds
    if names[vname]['dimensions'] == 3:
        ds["depth_bnds"] = zbnds
    if cbounds:
        ds["lon_bnds"] = xbnds
        ds["lat_bnds"] = ybnds
    now = datetime.datetime.now( ).isoformat( )
    ds.attrs['Conventions'] = "CF-1.11"
    ds.attrs['creation_date'] = now
    ds.attrs['tracking_id'] = 'hdl:21.14103/'+str(uuid.uuid4( ))
    ds.attrs['description'] = domain+' simulation'
    ds.attrs['title'] = 'Coupled RegCM-ES1-1 simulation. Ocean Component is MITgcm checkpoint69e. Output prepared for CORDEX experiment'
    ds.attrs['activity_id'] = 'CORDEX'
    ds.attrs['contact'] = 'ggiulian@ictp.it'
    ds.attrs['experiment_id'] = experiment
    ds.attrs['domain'] = 'Mediterranean'
    ds.attrs['domain_id'] = domain
    if not regular_ll_grid:
        ds.attrs['grid'] = 'MITgcm ORCA curvilinear tripolar grid at 1/12 degree resolution (MED-12)'
        
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
    ds.attrs['table_id'] = 'Table '+table_map.get(cfrq)
    ds.attrs['grid_label'] = 'gn'
    ds.attrs['frequency'] = cfrq
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

    # Append all MITgcm namelist parameters as global attributes so the
    # exact model configuration is self-documented in the NetCDF file.
    # Attribute names are prefixed with the namelist stem (e.g. mit_deltaTmom).
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

    if 'pickup' in vname:
        opath = '.'
    else:
        opath = os.path.join(outpath,'CORDEX-CMIP6','DD',domain,myinst,
              gmodel,experiment,gmemb,'RegCM-ES1-1','v1-r1',cfrq,
              infname)
        os.makedirs(opath,exist_ok=True)
    if cfrq == 'day':
      ncfile = os.path.join(opath, infname + '_' + domain + '_' + gmodel +
            '_' + experiment + '_' + gmemb + '_' + myinst +
            '_RegCM-ES1-1_v1-r1_'+cfrq+'_'+
            s_ym.strftime('%Y%m%d') + '-' + e_ym.strftime('%Y%m%d') + '.nc')
    else:
      ncfile = os.path.join(opath, infname + '_' + domain + '_' + gmodel +
            '_' + experiment + '_' + gmemb + '_' + myinst +
            '_RegCM-ES1-1_v1-r1_'+cfrq+'_'+
            s_ym.strftime('%Y%m') + '-' + e_ym.strftime('%Y%m') + '.nc')
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
    if 'pickup' in vname:
        continue
    else:
        try:
            os.mkdir('mitgcm_output')
        except:
            pass
        metafile = os.path.splitext(binfile)[0]+'.meta'
        try:
            os.rename(binfile, os.path.join('mitgcm_output',binfile))
            os.rename(metafile, os.path.join('mitgcm_output',metafile))
        except:
            try:
                shutil.move(binfile, os.path.join('mitgcm_output',binfile))
                shutil.move(metafile, os.path.join('mitgcm_output',metafile))
            except:
                pass
