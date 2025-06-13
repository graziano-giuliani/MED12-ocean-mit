#!/usr/bin/env python3

import sys

if len(sys.argv) < 3:
    print('Usage : '+sys.argv[0] + ' var_file1.nc [var_file2.nc]')
    sys.exit(-1)

import os
import cmocean
import numpy as np
import xarray
import regionmask
import geopandas
import matplotlib.pyplot as plt

xarray.set_options(keep_attrs=True)

#ocean_shapes = '/leonardo_work/ICT25_ESP/GIS/SeaVoX_sea_areas/SeaVoX_sea_areas_polygons_v19.shp'
#gdf = geopandas.read_file(ocean_shapes)
#geometries = gdf[REGION == 'MEDITERRANEAN REGION']
#geometries.to_file('Mediterraneo.shp')

colors = { "so"     : cmocean.cm.haline,
           "thetao" : cmocean.cm.thermal,
         }

ocean_shapes = 'Mediterraneo.shp'
gdf = geopandas.read_file(ocean_shapes)

try:
    variable = os.path.basename(sys.argv[1]).split('_')[0]
except:
    print('Cannot name the variable from ',sys.argv[1])
    sys.exit(-1)

try:
    xds = xarray.open_mfdataset(sys.argv[1:], decode_coords=all,
            concat_dim='time', combine='nested')
    lon = xds.lon
    lat = xds.lat
    var = xds[variable]
    long_name = var.long_name
    units = var.units
except:
    sys.exit(-1)

regions = regionmask.from_geopandas(gdf, names='SUB_REGION',
                       abbrevs='_from_name')
mask2d = regions.mask_3D(lon, lat)

for i, med_region in enumerate(gdf.itertuples()):
    subregion = med_region.SUB_REGION
    clipped = var.where(mask2d.isel(region=i), other=np.nan)
    clipped = clipped.mean(dim=('lat','lon'))
    p = clipped.dropna(dim="depth").sel(depth=slice(None,200.0)).plot(
            x="time",y="depth",cmap=colors[variable])
    p.axes.yaxis.set_inverted(True)
    plt.title(subregion.lower( ).capitalize( )+' '+long_name+' ['+units+']')
    oname = variable+'-'+'_'.join(subregion.lower( ).split())+'.png'
    oname = oname.translate(str.maketrans(',','_'))
    plt.savefig(oname)
    plt.close("all")
