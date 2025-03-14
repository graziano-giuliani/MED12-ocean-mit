#!/usr/bin/env python3

import os
import sys
import numpy as np
import xarray as xr

NX = 660
NY = 368

delz = [ 1.05073322312647, 1.16290298157928, 1.29084239390147, 
         1.43673151126053, 1.60304060113475, 1.79256540892385,
         2.00846567165814, 2.25430685033500, 2.53410491200126,
         2.85237380775375, 3.21417504627911, 3.62516844082599,
         4.09166269600144, 4.62066398484923, 5.21992003321097,
         5.89795646843153, 6.66410130199628, 7.52849241279829,
         8.50206181166293, 9.59648935947070, 10.8241175802607,
         12.1978184051993, 13.7308023080591, 15.4363606120969,
         17.3275330782464, 19.4166955701354, 21.7150669596920,
         24.2321407237791, 26.9750549307207, 29.9479242568679,
         33.1511686097878, 36.5808836631247, 40.2283074321641,
         44.0794418986593, 48.1148875626752, 52.3099400364761,
         56.6349807662321, 61.0561694929633, 65.5364166358181,
         70.0365833641819, 74.5168305070367, 78.9380192337679,
         83.2630599635239, 87.4581124373248, 91.4935581013408,
         95.3446925678359, 98.9921163368753, 102.421831390212,
         105.625075743132, 108.597945069279, 111.340859276221,
         113.857933040308, 116.156304429865, 118.245466921754,
         120.136639387903, 121.842197691941, 123.375181594801,
         124.748882419739, 125.976510640529, 127.070938188337,
         128.044507587202, 128.908898698004, 129.675043531568,
         130.353079966789, 130.952336015151, 131.481337303999,
         131.947831559174, 132.358824953721, 132.720626192246,
         133.038895087999, 133.318693149665, 133.564534328342,
         133.780434591076, 133.969959398865, 134.136268488739 ]

NZ = len(delz)

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

binfile = sys.argv[1]
name = os.path.splitext(binfile)[0]
ncfile = name + '.nc'

da = None
try:
    h = np.fromfile(sys.argv[1], '>f4').reshape(NY,NX)
    da = xr.DataArray(name = name, data = h, 
                dims = ["lon","lat"],
                coords = dict(lon = xlon,
                              lat = xlat),
                attrs = dict(standard_name = "unknown",
                             units = "1",
                             coordinates = "lat lon"),
                )
    da.to_netcdf(ncfile)
except:
    count = NZ*NY*NX
    try:
        h = np.fromfile(sys.argv[1], '>f4',
                count = count).reshape(NZ,NY,NX)
        da = xr.DataArray(name = name , data=h, 
                    dims = ["dz","lon","lat"],
                    coords = dict(lon = xlon,
                                  lat = xlat,
                                  dz = (["dz"],np.array(delz))),
                    attrs = dict(standard_name = "unknown",
                                 units = "1",
                                 coordinates = "lat lon"),
                    )
        da.to_netcdf(ncfile)
    except:
        xtime = xr.DataArray(name = "time",
                    data = np.array([0.0,]), 
                    dims = ["time"],
                    attrs = dict(standard_name = "time",
                        units = "days since 1970-01-01 00:00:00"))
        h = np.fromfile(sys.argv[1], '>f4',
                count = count).reshape(NZ,NY,NX)
        da = xr.DataArray(name = name , data=h, 
                    dims = ["time","dz","lon","lat"],
                    coords = dict(lon = xlon,
                                  lat = xlat,
                                  dz = (["dz"],np.array(delz)),
                                  time = xtime),
                    attrs = dict(standard_name = "unknown",
                                 units = "1",
                                 coordinates = "lat lon"),
                    )
        da.to_netcdf(ncfile, unlimited_dims="time")
