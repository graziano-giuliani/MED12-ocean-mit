#!/usr/bin/env python3

import xarray
import numpy as np

depthfile = '../grid/depth.nc'
bathyfile = 'BATHYMETRY.nc'

ds_depth = xarray.open_dataset(depthfile)
ds_bathy = xarray.open_dataset(bathyfile)

bathy = ds_bathy.elevation
lon = ds_bathy.lon
lat = ds_bathy.lat
mask = ds_bathy.mask

(ny,nx) = np.shape(lon)
nz = len(ds_depth.depth)

dpth = ds_depth.depth.data
thick = ds_depth.cell_thickness.data

limit = dpth

arr_2d = np.repeat(limit[:,np.newaxis],ny,axis=1)
arr_3d = np.repeat(arr_2d[:,:,np.newaxis],nx,axis=2)
dpth3d = np.repeat(bathy.data[np.newaxis,:,:],nz,axis=0)
mask3d = np.logical_and(dpth3d < 0,arr_3d <= -dpth3d)
dm3d = np.where(mask3d,1.0,np.nan)

mask3d = xarray.DataArray(name = 'mask3d', data = dm3d,
        dims = ["depth", "y", "x"],
        coords = dict(lon=lon, lat=lat, depth=ds_depth.depth),
        attrs = dict(standard_name = 'sea_binary_mask',
                     long_name = '3D sea binary mask',
                     units = '1',
                     coordinates = 'lat lon')
        )
ds = mask3d.to_dataset( )
ds.attrs['Conventions'] = "CF-1.9"
encode = { 'mask3d' : { 'zlib': True,
                           'complevel' : 6,
                      }
         }
ds.to_netcdf('mask3d.nc', format = 'NETCDF4', encoding = encode)
