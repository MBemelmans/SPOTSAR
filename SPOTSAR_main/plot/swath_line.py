from skspatial.objects import Line as sksline
import scipy.spatial.transform 

import json
from shapely.geometry import Polygon
from shapely.geometry import Point, LineString, mapping
from functools import partial
from shapely.ops import transform
import pyproj


def swath_line(line_coords,width):
    line = LineString(line_coords)
    local_azimuthal_projection = f"+proj=aeqd +R=6371000 +units=m +lat_0={line.coords[0][1]} +lon_0={line.coords[0][0]}"

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
    line_transformed = transform(wgs84_to_aeqd, line)
    buffer_line = line_transformed.buffer(width/2,cap_style=2)# capstyle 2 for flat caps the meet profile (so do not go beyond the line)
    return transform(aeqd_to_wgs84, buffer_line)