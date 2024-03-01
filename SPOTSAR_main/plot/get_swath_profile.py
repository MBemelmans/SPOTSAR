import numpy as np
from inpoly import inpoly2 # for fast inpolygon checks
from skspatial.objects import Line as sksline
import scipy.spatial.transform 

from .swath_line import swath_line
from .geodetic2enu import geodetic2enu


import contextlib
import shapely
import warnings
from distutils.version import LooseVersion

SHAPELY_GE_20 = str(shapely.__version__) >= LooseVersion("2.0")

try:
    from shapely.errors import ShapelyDeprecationWarning as shapely_warning
except ImportError:
    shapely_warning = None

if shapely_warning is not None and not SHAPELY_GE_20:
    @contextlib.contextmanager
    def ignore_shapely2_warnings():
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=shapely_warning)
            yield
else:
    @contextlib.contextmanager
    def ignore_shapely2_warnings():
        yield


def get_swath_profile(data,lons,lats,start,end,width=25,dx=10,):
    """ Calculate swarth profile for gridded or 1-d array data with known longitude,latitude coordinates.


    Arguments:
        data  (np.array)        : Data from which swath profile is taken.
        lon   (np.array)        : Longitude of the data.
        lat   (np.array)        : Latitude of data.
        start (np.array-like)   : (longitude, latitude) of start point of swath profile
        end   (np.array-like)   : (longitude, latitude) of end point of swath profile
        width (float or int)    : (optional) width of swarth profile in meters, defaults to 25
        dx    (float or int)    : (optional) along profile discretisation in meters, detaults to 10 m

    Return:
        proj_data     (np.array)      : array containing, longitude, latitude, distance along profile, data
        profile_stats (np.array)      : array containing distance along profile, mean, median, 2.5 percentile, 97.5 percentile
    """

    # define swath profile centre line
    line = sksline.from_points(point_a=start, point_b=end)
    line_coords = np.asarray([start,end])
    buffer_poly = swath_line(line_coords,width)

    # stack lon and lat
    lon_lat = np.dstack((lons,lats))

    # get data within swath profile
    isin, ison = inpoly2(np.squeeze(lon_lat),np.asarray(buffer_poly.exterior.coords))
    print(f'number of points in swath profile: {np.count_nonzero(isin)}')
    proj_point = np.empty(shape=(np.count_nonzero(isin), 3), dtype=float) # pre-alloc nd-array 

    with ignore_shapely2_warnings():
        for p_id, lon_lat_id in enumerate(zip(np.squeeze(lon_lat)[isin,:],data.flatten()[isin])):
            point = lon_lat_id[0]
            proj_point[p_id,:]=np.append(np.asarray(line.project_point(point)),lon_lat_id[1])

    # transform projected points to east,north,(up)
    point_transformed = geodetic2enu(proj_point[:,1],
                                    proj_point[:,0],
                                    np.squeeze(np.zeros((np.count_nonzero(isin),1))).T,
                                    start[1],
                                    start[0],
                                    0)
    
    #lon,lat,dist along profile, data
    proj_data      = np.stack((proj_point[:,0], 
                            proj_point[:,1],
                            np.linalg.norm(point_transformed[:,0:2],axis=1),
                            proj_point[:,2])).T


    # calculate statistics along swath profile with sections of length dx
    max_dist = proj_data[:,2].max()
    edges = np.arange(0,max_dist,dx)
    profile_stats = np.empty(shape=(edges.shape[0]-1, 5), dtype=float) # pre-alloc nd-array
    for bin_id in enumerate(edges[:-1]):
        sel = np.squeeze(np.asarray([(proj_data[:,2]>=edges[bin_id[0]]) & (proj_data[:,2]<=edges[bin_id[0]+1])]))
        profile_stats[bin_id[0],:] = [bin_id[1]+dx/2,
                                      np.nanmean(proj_data[sel,3]),
                                      np.nanmedian(proj_data[sel,3]),
                                      np.nanpercentile(proj_data[sel,3],2.5),
                                      np.nanpercentile(proj_data[sel,3],97.5)]

    return proj_data, profile_stats