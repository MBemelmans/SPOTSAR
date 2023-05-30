import pyproj
# from pyproj import CRS
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.geometry.point import Point


def get_1deg_dist():
    """ Get distance of 1 degree of a great circle 
        for plotting scalebars in figures
    """
    crs = pyproj.CRS('EPSG:4326')
    points = gpd.GeoSeries([Point(110, -7.5), Point(111, -7.5)],crs=crs)
    points = points.to_crs(32750) # Projected WGS 84 - meters
    return points[0].distance(points[1])