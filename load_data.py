### import external packages
import numpy as np
import pandas as pd

import numba
from numba import vectorize
import glob  # for file search
import copy
import os  # operating system stuff
import re  # regex
import fastparquet  # fast read/write for large data structures
import sklearn.preprocessing as pre  # for data normalisation
from sklearn.metrics import pairwise_distances

import geopandas as gpd
import rasterio as rio
import rasterio.mask
from rasterio.plot import plotting_extent
from shapely.geometry import Polygon
from shapely.geometry.point import Point
import pyproj
from pyproj import CRS
from inpoly import inpoly2  # for fast inpolygon checks
import utm

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm as mpl_cm
from matplotlib import colors as mcolors

from mpl_toolkits.axes_grid1 import make_axes_locatable  # for colorbar scaling
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter

import seaborn as sns
from matplotlib import rc_file_defaults

rc_file_defaults()
# sns.set(style=None, color_codes=True)

from shapely.geometry import Polygon
from shapely.geometry.point import Point
import datetime

import configparser

from cmcrameri import cm  # for scientific colourmaps

###########################
# import main local package
import SPOTSAR_main as sm


### define constants

################ Define user INPUTS #######################
######## please edit the values of this block only ########
###########################################################

# define hillshade file
HS_FILE = "./test_data/DEM/TDX_Merapi_WGS84_HS.tif"

# define lon and lat files
LON_FILE = "./test_data/CSK_dsc/geo2/20200910.lon"
LAT_FILE = "./test_data/CSK_dsc/geo2/20200910.lat"

# define parameter text file
PARAM_FILE = "./test_data/CSK_dsc/params.txt"

# define map region of interest
lon_lims = [110.425, 110.45]
lat_lims = [-7.555, -7.535]

# define colour range {min max} (min = -max)
vmax = 3  # range of colourscale in meters

# define file names for data, lon and lat
DIRECTORY_PATH = "./test_data/CSK_dsc/DISP_txt2/"
# define path to ccp and ccs files
DIRECTORY_PATH_CCS = "./test_data/CSK_dsc/CCS2/"


def get_image_pairs(folder_path, regex_str, length):
    # Get a list of all files in the folder
    files = os.listdir(folder_path)
    print("number of files:", np.size(files))

    # Define the regular expression pattern
    pattern = re.compile(regex_str)

    # Filter and sort files based on the first 11 characters
    sorted_files = sorted(
        [file for file in files if pattern.match(file)], key=lambda x: x[:length]
    )
    print("number of files mathing pattern:", np.size(sorted_files))

    unique_files = []
    for file in sorted_files:
        if file[:length] not in unique_files:
            unique_files.append(file[:length])

    print("number of unique image pairs:", np.size(unique_files))
    return unique_files


# Example usage
pair_names = get_image_pairs(
    DIRECTORY_PATH, r"c[0-9]+_c[0-9]+_disp_[0-9]+_[0-9]+.txt", 19
)


# open hillshade file and re-order offset and CCS files

# open hill shade file with rasterio
DEM_HS = rio.open(HS_FILE)
SHADING = DEM_HS.read(1, masked=True)  # rasterio bands are indexed from 1

# extract DEM extent
DEM_EXTENT = [
    DEM_HS.bounds.left,
    DEM_HS.bounds.right,
    DEM_HS.bounds.bottom,
    DEM_HS.bounds.top,
]

# read parameters from text file
config = configparser.ConfigParser()
config.read(PARAM_FILE)
WIDTH = int(config.get("params", "width"))
LINES = int(config.get("params", "lines"))
WIDTH_CCS = int(config.get("params", "width_ccs"))
LINES_CCS = int(config.get("params", "lines_ccs"))
R_START = int(config.get("params", "r_start"))
A_START = int(config.get("params", "a_start"))
R_STEP = int(config.get("params", "r_step"))
A_STEP = int(config.get("params", "a_step"))
HEADING = float(config.get("params", "heading"))
MEAN_INC = float(config.get("params", "mean_inc"))
