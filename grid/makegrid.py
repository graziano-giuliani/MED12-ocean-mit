#!/usr/bin/env python3

import os
import sys
import datetime
import yaml
import numpy as np
from netCDF4 import Dataset

def radius(lat):
    B = np.radians(lat) #converting into radians
    a = 6378137.0  #Radius at sea level at equator
    b = 6356752.0  #Radius at poles
    c = (a**2*np.cos(B))**2
    d = (b**2*np.sin(B))**2
    e = (a*np.cos(B))**2
    f = (b*np.sin(B))**2
    R = np.sqrt((c+d)/(e+f))
    return R

def compute_areas(centerlat,bottomleftlat,bottomrightlat,toprightlat,topleftlat,
       centerlon,bottomleftlon,bottomrightlon,toprightlon,topleftlon):
    area = np.zeros_like(centerlat)
    R = radius(centerlat)
    for i in range(area.shape[0]):
        for j in range(area.shape[1]):
            lats = (bottomleftlat[i,j],bottomrightlat[i,j],
                    toprightlat[i,j],topleftlat[i,j])
            lons = (bottomleftlon[i,j],bottomrightlon[i,j],
                    toprightlon[i,j],topleftlon[i,j])
            area[i,j] = polygon_area(lats,lons,R[i,j])
    return area

def polygon_area(ilats, ilons, radius = 6378137):
    """
    Computes area of spherical polygon, assuming spherical Earth.
    Returns result in ratio of the sphere's area if the radius is specified.
    Otherwise, in the units of provided radius.
    lats and lons are in degrees.
    """
    lats = np.deg2rad(ilats)
    lons = np.deg2rad(ilons)

    # Line integral based on Green's Theorem, assumes spherical Earth

    #close polygon
    if lats[0]!=lats[-1]:
        lats = np.append(lats, lats[0])
        lons = np.append(lons, lons[0])

    #colatitudes relative to (0,0)
    a = np.sin(lats/2)**2 + np.cos(lats)* np.sin(lons/2)**2
    colat = 2*np.arctan2( np.sqrt(a), np.sqrt(1-a) )

    #azimuths relative to (0,0)
    az = np.arctan2(np.cos(lats) * np.sin(lons), np.sin(lats)) % (2*np.pi)

    # Calculate diffs
    # daz = np.diff(az) % (2*np.pi)
    daz = np.diff(az)
    daz = (daz + np.pi) % (2 * np.pi) - np.pi

    deltas = np.diff(colat)/2
    colat = colat[0:-1]+deltas

    # Perform integral
    integrands = (1-np.cos(colat)) * daz

    # Integrate
    area = abs(sum(integrands))/(4*np.pi)

    area = min(area,1-area)
    if radius is not None: #return in units of radius
        return area * 4*np.pi*radius**2
    else: #return in ratio of sphere total area
        return area

try:
    with open(sys.argv[1],"r") as f:
        config = yaml.safe_load(f)
except:
    try:
        with open("makegrid.yaml","r") as f:
            config = yaml.safe_load(f)
    except:
        print("Cannot open configuration file " + sys.argv[1])
        sys.exit(1)

ofile = config["ofile"]
grid_type = config["grid_type"]
output_2d = config["output_2d"]

if grid_type == "regular_latlon":
    resolution = config["regular_latlon"]["resolution"]
    dlon = resolution
    dlat = resolution
    lon1 = config["regular_latlon"]["west_longitude"]
    lon2 = config["regular_latlon"]["east_longitude"]
    lat1 = config["regular_latlon"]["south_latitude"]
    lat2 = config["regular_latlon"]["north_latitude"]
    lon = np.arange(lon1,lon2+dlon/2,dlon)
    lat = np.arange(lat1,lat2+dlat/2,dlat)
    nlon = lon.size
    nlat = lat.size
    dhlat = dlat/2.0
    dhlon = dlon/2.0
    centerlat = np.repeat(lat,nlon).reshape((nlat,nlon))
    centerlon = np.repeat(lon,nlat).reshape((nlon,nlat)).T
    bottomleftlat = centerlat-dhlat
    bottomleftlon = centerlon-dhlon
    bottomrightlat = centerlat-dhlat
    bottomrightlon = centerlon+dhlon
    toprightlat = centerlat+dhlat
    toprightlon = centerlon+dhlon
    topleftlat = centerlat+dhlat
    topleftlon = centerlon-dhlon
    cellarea = compute_areas(centerlat,bottomleftlat,bottomrightlat,
            toprightlat,topleftlat,centerlon,bottomleftlon,bottomrightlon,
            toprightlon,topleftlon)
elif grid_type == "orca_grid":
    infile = config["orca_grid"]["gridfile"]
    ds = Dataset(infile,'r')
    centerlon = ds.variables['nav_lon'][1:-1,1:-1].data
    centerlat = ds.variables['nav_lat'][1:-1,1:-1].data
    glamu = ds.variables['glamu'][:].data # long
    gphiv = ds.variables['gphiv'][:].data # latg
    dxf  = ds.variables['e1t'][0,1:-1,1:-1].data
    dyf  = ds.variables['e2t'][0,1:-1,1:-1].data
    ds.close( )
    nlat, nlon = centerlon.shape
    bottomleftlat = gphiv[0,0:-2,0:-2]
    bottomrightlat = gphiv[0,0:-2,1:-1]
    toprightlat = gphiv[0,1:-1,1:-1]
    topleftlat = gphiv[0,1:-1,0:-2]
    bottomleftlon = glamu[0,0:-2,0:-2]
    bottomrightlon = glamu[0,0:-2,1:-1]
    toprightlon = glamu[0,1:-1,1:-1]
    topleftlon = glamu[0,1:-1,0:-2]
    cellarea = dxf*dyf
elif grid_type == "scrip_grid":
    infile = config["scrip_grid"]["gridfile"]
    ds = Dataset(infile,'r')
    shape = ds.variables['grid_dims'][:]
    nlat,nlon = shape.tolist( )
    centerlon = ds.variables['grid_center_lon'][:].data.reshape(shape)
    centerlat = ds.variables['grid_center_lat'][:].data.reshape(shape)
    clat = ds.variables['grid_corner_lat']
    clon = ds.variables['grid_corner_lon']
    bottomleftlat = clat[:,0].reshape(shape)
    bottomrightlat = clat[:,1].reshape(shape)
    toprightlat = clat[:,2].reshape(shape)
    topleftlat = clat[:,3].reshape(shape)
    bottomleftlon = clon[:,0].reshape(shape)
    bottomrightlon = clon[:,1].reshape(shape)
    toprightlon = clon[:,2].reshape(shape)
    topleftlon = clon[:,3].reshape(shape)
    ds.close( )
    cellarea = compute_areas(centerlat,bottomleftlat,bottomrightlat,
            toprightlat,topleftlat,centerlon,bottomleftlon,bottomrightlon,
            toprightlon,topleftlon)

with Dataset(ofile, "w") as dst:

    dst.title = 'SCRIP gridfile'
    dst.gridtype = 'cell'
    dst.datetime = datetime.datetime.now(datetime.UTC).isoformat( )

    if output_2d:
        # Define dimension
        dst.createDimension("grid_rank",2)
        dst.createDimension("grid_size",nlon*nlat)
        dst.createDimension("grid_xsize",nlon)
        dst.createDimension("grid_ysize",nlat)
        dst.createDimension("grid_corners",4)

        # Define variables
        grid_dims = dst.createVariable("grid_dims", 'i4', ["grid_rank",])
        grid_center_lon = dst.createVariable("grid_center_lon", 'f4',
                ["grid_ysize", "grid_xsize"])
        grid_center_lon.standard_name = "longitude"
        grid_center_lon.long_name = "Longitude"
        grid_center_lon.units = "degrees_east"
        grid_center_lon.bounds = "grid_corner_lon"
        grid_center_lat = dst.createVariable("grid_center_lat", 'f4',
                ["grid_ysize", "grid_xsize"])
        grid_center_lat.standard_name = "latitude"
        grid_center_lat.long_name = "Latitude"
        grid_center_lat.units = "degrees_north"
        grid_center_lat.bounds = "grid_corner_lat"
        grid_cell_area = dst.createVariable("cell_area", 'f4',
                ["grid_ysize", "grid_xsize"])
        grid_cell_area.standard_name = "cell_area"
        grid_cell_area.long_name = "Horizontal Area of gridcell"
        grid_cell_area.units = "m2"
        grid_cell_area.coordinates = "grid_center_lat grid_center_lon"
        grid_corner_lon = dst.createVariable("grid_corner_lon", 'f4',
                ["grid_ysize", "grid_xsize", "grid_corners"])
        grid_corner_lon.standard_name = "longitude_bounds"
        grid_corner_lon.long_name = "Longitude Bounds"
        grid_corner_lon.units = "degrees_north"
        grid_corner_lon.coordinates = "grid_center_lat grid_center_lon"
        grid_corner_lat = dst.createVariable("grid_corner_lat", 'f4',
                ["grid_ysize", "grid_xsize", "grid_corners"])
        grid_corner_lat.standard_name = "latitude_bounds"
        grid_corner_lat.long_name = "Latitude Bounds"
        grid_corner_lat.units = "degrees_north"
        grid_corner_lat.coordinates = "grid_center_lat grid_center_lon"

        # Write variables in file
        grid_dims[:] = np.array((nlon,nlat))
        grid_center_lat[:] = centerlat
        grid_center_lon[:] = centerlon
        grid_corner_lat[:,:,0] = bottomleftlat
        grid_corner_lat[:,:,1] = bottomrightlat
        grid_corner_lat[:,:,2] = toprightlat
        grid_corner_lat[:,:,3] = topleftlat
        grid_corner_lon[:,:,0] = bottomleftlon
        grid_corner_lon[:,:,1] = bottomrightlon
        grid_corner_lon[:,:,2] = toprightlon
        grid_corner_lon[:,:,3] = topleftlon
        grid_cell_area[:] = cellarea
    else:
        # Define dimension
        dst.createDimension("grid_rank",2)
        dst.createDimension("grid_size",nlon*nlat)
        dst.createDimension("grid_corners",4)

        # Define variables
        grid_dims = dst.createVariable("grid_dims", 'i4', ["grid_rank",])
        grid_center_lon = dst.createVariable("grid_center_lon", 'f4',
                ["grid_size"])
        grid_center_lon.standard_name = "longitude"
        grid_center_lon.long_name = "Longitude"
        grid_center_lon.units = "degrees_east"
        grid_center_lon.bounds = "grid_corner_lon"
        grid_center_lat = dst.createVariable("grid_center_lat", 'f4',
                ["grid_size"])
        grid_center_lat.standard_name = "latitude"
        grid_center_lat.long_name = "Latitude"
        grid_center_lat.units = "degrees_north"
        grid_center_lat.bounds = "grid_corner_lat"
        grid_cell_area = dst.createVariable("cell_area", 'f4',
                ["grid_size"])
        grid_cell_area.standard_name = "cell_area"
        grid_cell_area.long_name = "Horizontal Area of gridcell"
        grid_cell_area.units = "m2"
        grid_corner_lon = dst.createVariable("grid_corner_lon", 'f4',
                ["grid_size", "grid_corners"])
        grid_corner_lon.standard_name = "longitude_bounds"
        grid_corner_lon.long_name = "Longitude Bounds"
        grid_corner_lon.units = "degrees_north"
        grid_corner_lat = dst.createVariable("grid_corner_lat", 'f4',
                ["grid_size", "grid_corners"])
        grid_corner_lat.standard_name = "latitude_bounds"
        grid_corner_lat.long_name = "Latitude Bounds"
        grid_corner_lat.units = "degrees_north"

        # Write variables in file
        grid_dims[:] = np.array((nlon,nlat))
        grid_center_lat[:] = centerlat.flatten( )
        grid_center_lon[:] = centerlon.flatten( )
        grid_corner_lat[:,0] = bottomleftlat.flatten( )
        grid_corner_lat[:,1] = bottomrightlat.flatten( )
        grid_corner_lat[:,2] = toprightlat.flatten( )
        grid_corner_lat[:,3] = topleftlat.flatten( )
        grid_corner_lon[:,0] = bottomleftlon.flatten( )
        grid_corner_lon[:,1] = bottomrightlon.flatten( )
        grid_corner_lon[:,2] = toprightlon.flatten( )
        grid_corner_lon[:,3] = topleftlon.flatten( )
        grid_cell_area[:] = cellarea.flatten( )

print('Done')
