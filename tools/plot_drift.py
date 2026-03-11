#!/usr/bin/env python3

import sys
import os
import glob
import pathlib
import itertools
import numpy as np
import geopandas
import regionmask
import xarray as xr
import matplotlib.pyplot as plt

depths = [ { 'name'   : 'bottom',
             'top'    : 2000,
             'bottom' : None, },
           { 'name'   : 'middle',
             'top'    : 500,
             'bottom' : 1000, },
           { 'name'   : 'surface',
             'top'    : None,
             'bottom' : 200, },
         ]

paths = [ 'initial', 'loop?' ]

sdir = pathlib.Path(sys.argv[1]) 
bases = sys.argv[2:]

ocean_shapes = 'Mediterraneo.shp'
gdf = geopandas.read_file(ocean_shapes)
regions = regionmask.from_geopandas(gdf, names='SUB_REGION',
              abbrevs='_from_name')

for base in bases:
    patterns = ( os.path.join(x,'CORDEX-CMIP6','**',
                        base,base+'*.nc') for x in paths )
    matched_paths = list(
      itertools.chain.from_iterable(sdir.glob(pattern)
          for pattern in patterns) )
    print(len(matched_paths))

    ds = xr.load_dataset(matched_paths[0])
    lat = ds['lat'][:]
    lon = ds['lon'][:]
    long_name = ds[base].long_name
    units = ds[base].units
    ds.close( )

    mask2d = regions.mask_3D(lon, lat)
    ds = xr.open_mfdataset(sorted(matched_paths), combine='nested',
             concat_dim="time", data_vars='minimal', compat='no_conflicts')
    var = ds[base]
    for i, med_region in enumerate(gdf.itertuples()):
        subregion = med_region.SUB_REGION
        if 'depth' in var.dims:
            for d in depths:
                xx = var.where(mask2d.isel(region=i), other=np.nan).sel(
                  depth=slice(d['top'],d['bottom']))
                if ( len(ds.time) > 24 ):
                    xv = xx.mean(dim=('lat','lon',
                                 'depth')).groupby("time.month")
                    vv = xv-xv.mean(dim="time")
                else:
                    vv = xx.mean(dim=('lat','lon','depth')) 
                vv = vv-vv[0]
                if np.sum(~np.isnan(vv)) > 0:
                    print(subregion+' : '+d['name'])
                    plt.plot(vv)
                    plt.title(subregion.lower( ).capitalize( )+'\n'+
                      long_name+' anomaly ['+units+']\n'+d['name']+' depth ['+
                      repr(d['top'])+'-'+repr(d['bottom'])+']')
                    oname = base+'-'+'_'.join(subregion.lower( ).split())
                    oname = oname.translate(str.maketrans(',','_'))
                    oname = oname+'_'+d['name']+'.png'
                    plt.savefig(oname)
                    plt.close("all")
        else:
            xx = var.where(mask2d.isel(region=i), other=np.nan)
            if ( len(ds.time) > 24 ):
                xv = xx.mean(dim=('lat','lon')).groupby("time.month")
                vv = xv-xv.mean(dim="time")
            else:
                vv = xx.mean(dim=('lat','lon'))
            vv = vv-vv[0]
            if np.sum(~np.isnan(vv)) > 0:
                print(subregion+' : surface')
                plt.plot(vv)
                plt.title(subregion.lower( ).capitalize( )+'\n'+
                    long_name+' anomaly ['+units+']')
                oname = base+'-'+'_'.join(subregion.lower( ).split())
                oname = oname.translate(str.maketrans(',','_'))
                oname = oname+'.png'
                plt.savefig(oname)
                plt.close("all")
    ds.close( )
