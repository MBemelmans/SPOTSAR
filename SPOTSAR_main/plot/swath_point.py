
import numpy as np
import json
import pyproj
from shapely.geometry import Point, LineString, mapping
from functools import partial
from shapely.ops import transform




def swath_point(point,r):
    ##
    # function transforms query point (lon,lat)WGS84 into 
    # local azimuthal projection (rect-linear with minimum local distortion)
    # then applies a buffer of desired radius in meters to that point 
    # and makes a n-gon polygonal apprixomation of a circle 
    n=128
    point = Point(point[0], point[1])
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

    circle_coords = np.asarray(transform(aeqd_to_wgs84, buffer).exterior.coords)

    return circle_coords

### usage:
# # use inpoly2 for very fast in polygon check
# q_point = [110.44, -7.541]
# circle_coords = swath_point(q_point,25)
# isin, ison = inpoly2(np.squeeze(lon_lat),coordinates_circle)