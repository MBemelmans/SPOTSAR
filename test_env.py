# import external packages
import numpy as np
import pandas as pd

# import numba
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

# from matplotlib import rc_file_defaults
# rc_file_defaults()
# sns.set(style=None, color_codes=True)


from shapely.geometry import Polygon
from shapely.geometry.point import Point
import datetime

import configparser

from cmcrameri import cm  # for scientific colourmaps

if __name__ == "__main__":
    print("imports done")
