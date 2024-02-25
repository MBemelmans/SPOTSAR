import numpy as np
import geopandas as gpd

def read_line_shp(filename):
    """ reads a .shp file containing lines (i.e. coordinates stored in [geometry].coords)
        Args:
        finename (str): .shp filename

        Returns:
        coords (list | list of lists): coordinates of points defining the line
    """
    line_shp = gpd.read_file(filename)
    coords_list = []
    for i, line in enumerate(line_shp["geometry"]):
        coords = np.array(list(line.coords))
        coords_list.append(coords)
    
    if np.size(coords_list)==1:
        return coords
    else:
        return coords_list