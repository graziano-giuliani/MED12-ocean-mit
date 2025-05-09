#!/usr/bin/env python3

import os
import sys
import numpy as np
import xarray as xr

start_simulation = "1979-08-01 00:00:00 UTC"
timestep = 150

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

NX = 660
NY = 368
NZ = len(depth)

for binfile in sys.argv[1:]:
    name = os.path.basename(os.path.splitext(binfile)[0])
    ncfile = name + '.nc'
    vname,vdate = name.split('.')

    time = float(vdate)*timestep

    lonfile = 'LONC.bin'
    latfile = 'LATC.bin'

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
                        data = depth, 
                        dims = ["depth"],
                        attrs = dict(standard_name = "depth",
                                     units = "m"))
    xtime = xr.DataArray(name = "time",
                         data = np.array((time,)),
                         dims = ["time"],
                         attrs = dict(standard_name = "time",
                                      units = "seconds since "+start_simulation))

    count = NZ*NY*NX
    h = np.fromfile(binfile, '>f4',
                    count = count).reshape(1,NZ,NY,NX)
    da = xr.DataArray(name = vname , data=h, 
                      dims = ["time","depth","lon","lat"],
                      coords = dict(lon = xlon,
                                    lat = xlat,
                                    depth = xdepth,
                                    time = xtime),
                      attrs = dict(standard_name = "Temperature",
                                   long_name = "Ocean temperature",
                                   units = "Celsius",
                                   coordinates = "lat lon"),
                     )
    da.to_netcdf(ncfile)
