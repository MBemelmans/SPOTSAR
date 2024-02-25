import numpy as np
from inpoly import inpoly2
from shapely.geometry import Polygon
from shapely.geometry.point import Point
import rasterio as rio
from sklearn import linear_model

import json
import pyproj
from shapely.geometry import Point, LineString, mapping
from functools import partial
from shapely.ops import transform


def query_point(lats,lons,q_lats,q_lons,r):
    """calculatess mean, median, standard deviation and 95% confidence interval 
    for attribute data within r radius of query points

    Args:
        lats (np.array): latitude of all points
        lons (np.array): longitude of all points
        attr (np.array): attribute value of all points
        q_lats (np.array): list of query point latitudes
        q_lons (np.array): list of query point longitudes
        r (float): search radius in meters
    """

    ##
    # function transforms query point (lon,lat)WGS84 into 
    # local azimuthal projection (rect-linear with minimum local distortion)
    # then applies a buffer of desired radius in meters to that point 
    # and makes a n-gon polygonal apprixomation of a circle 
    n=128
    lon_lat = np.transpose(np.stack((lons,lats)))
    q_mean = np.empty(np.shape(q_lats))
    q_median = np.empty(np.shape(q_lats))
    q_std = np.empty(np.shape(q_lats))
    q_95 = np.empty((np.size(q_lats),2))
    coordinate_circle_list = []
    if np.size(q_lons) == 1:
        q_lons = [q_lons]
        q_lats = [q_lats]
        
    isin_list = []
    for i, (q_lon, q_lat) in enumerate(zip(q_lons,q_lats)):
        point = Point(q_lon, q_lat)
        local_azimuthal_projection = f"+proj=aeqd +R=6371000 +units=m +lat_0={point.y} +lon_0={point.x}"

        wgs84_to_aeqd = partial(
            pyproj.transform,
            pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
            pyproj.Proj(local_azimuthal_projection),
        )

        aeqd_to_wgs84 = partial(
            pyproj.transform,
            pyproj.Proj(local_azimuthal_projection),
            pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
        )

        point_transformed = transform(wgs84_to_aeqd, point)

        buffer = point_transformed.buffer(r,n)# n-gon approximation
        circle_poly = transform(aeqd_to_wgs84, buffer)
        coordinates_circle= np.asarray(circle_poly.exterior.coords)
        coordinate_circle_list.append(coordinates_circle)

        # use inpoly2 for very fast in polygon check
        isin, ison = inpoly2(lon_lat,coordinates_circle)
        isin_list.append([isin])
    
    return isin, ison, coordinate_circle_list
