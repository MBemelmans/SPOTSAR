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

from .geodetic2enu import geodetic2enu

def query_point(lats,lons,data_attr,q_lats,q_lons,r,verbose=False):
    """calculatess mean, median, standard deviation and 95% confidence interval 
    for attribute data within r radius of query points

    Args:
        lats (_type_): latitude of all points
        lons (_type_): longitude of all points
        attr (_type_): attribute value of all points
        q_lats (_type_): list of query point latitudes
        q_lons (_type_): list of query point longitudes
        r (_type_): search radius in meters
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


        # deramp data
        # val = a*lat + b*lon + mean
        enu_vec = geodetic2enu(lats[isin],lons[isin],np.zeros(np.shape(lats[isin])),q_lat,q_lon,0)

        enu = np.reshape(enu_vec,[np.size(lats[isin]),3])
        local_east = enu[:,0]
        local_north = enu[:,1]

        X_data = np.transpose(np.stack((local_east,local_north)))
        Y_data = data_attr[isin]
        X_data = X_data[np.where(~np.isnan(Y_data))]
        Y_data = Y_data[np.where(~np.isnan(Y_data))]
        

        reg = linear_model.LinearRegression().fit(X_data, Y_data)
        if verbose:
            print("coefficients of equation of plane, (a1, a2): ", reg.coef_)
            print("value of intercept, c:", reg.intercept_)

        deramped_attr = data_attr[isin] - local_east * reg.coef_[0] - local_north * reg.coef_[1]

        # calculate statistics
        # mean
        q_mean[i] = np.nanmean(deramped_attr)
        q_median[i] = np.nanmedian(deramped_attr)
        q_std[i] = np.nanstd(deramped_attr)
        q_95[i,:] = [np.nanpercentile(deramped_attr,2.5),np.nanpercentile(deramped_attr,97.5)]

    return q_mean, q_median, q_std, q_95, coordinate_circle_list