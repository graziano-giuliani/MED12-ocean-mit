#!/usr/bin/env python3

import numpy as np
import regionmask
import geopandas
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

plt.rcParams['figure.figsize'] = (30.0, 10.0)
text_kws = dict(
       bbox=dict(color="none"),
       path_effects=[pe.withStroke(linewidth=2, foreground="w")],
       color="#67000d",
       fontsize=8,)

ocean_shapes = 'Mediterraneo.shp'
gdf = geopandas.read_file(ocean_shapes)
regions = regionmask.from_geopandas(gdf, names='SUB_REGION',
                                    abbrevs='_from_name')
regions.plot(add_ocean=True,
             resolution="50m",
             label="name",
             text_kws=text_kws)
plt.title('Mediterranenan Regions')
plt.savefig('Mediterranean_regions.png', bbox_inches='tight')

