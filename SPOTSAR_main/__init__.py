
import numpy as np
import pandas as pd
import glob # for file search
import copy
import os # operating system stuff
import re # regex
import fastparquet # fast read/write for large data structures
import sklearn.preprocessing as pre # for data normalisation
from sklearn.metrics import pairwise_distances

from rasterio.plot import plotting_extent
from shapely.geometry import Polygon
from shapely.geometry.point import Point
from pyproj import CRS
from inpoly import inpoly2 # for fast inpolygon checks



import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from matplotlib import cm as mpl_cm
from matplotlib import colors as mcolors 

from mpl_toolkits.axes_grid1 import make_axes_locatable # for colorbar scaling
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import FormatStrFormatter

import seaborn as sns
from matplotlib import rc_file_defaults
rc_file_defaults()
# sns.set(style=None, color_codes=True)

import pandas as pd
import geopandas as gpd
# !pip install utm
import utm

from shapely.geometry import Polygon
from shapely.geometry.point import Point
import datetime
import pyproj
from pyproj import CRS
import rasterio as rio
import rasterio.mask
from rasterio.plot import plotting_extent
from inpoly import inpoly2 # for fast inpolygon checks



import sklearn.preprocessing as pre # for data normalisation
from sklearn.metrics import pairwise_distances

from cmcrameri import cm # for scientific colourmaps

from . import Post_processing
from . import plot
from . import TS_processing
from . import misc_func
# from . import tutorials
