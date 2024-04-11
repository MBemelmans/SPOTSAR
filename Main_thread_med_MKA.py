### Title: Main script for performing bulk post-processing on SAR offset estimates computed with GAMMA.
### Author: Mark Bemelmans
### Date created: 2023-11-05
### Last updated: 2024-02-29
############################
############################
#### structure overview ####
# 1: load dependencies
# 2: define/load parameters
# 3: load data
# 4: load data into 
#    single_kernel and 
#    multi-kernel classes
# 5: filter outliers
# 6: multi-kernel averaging
# 7: save to hdf5 files
#############################

# 1: load dependencies
#  import external packages
import sys
sys.path.append('/Applications/anaconda3/envs/PhD_clean/lib/python3.11/site-packages/')

# general packages
import numpy as np
import pandas as pd
import glob  # for file search
import copy # to create hard copies of data
import os  # operating system stuff
import re  # regex

# geospatial packages
import geopandas as gpd 
import rasterio as rio 
import rasterio.mask 
from rasterio.plot import plotting_extent
from shapely.geometry import Polygon 
from shapely.geometry.point import Point 
import pyproj
from pyproj import CRS
import utm

# plotting and visualisation packages
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
rc_file_defaults() # reset Matplotlib defaults after loading seaborn
from cmcrameri import cm  # for scientific colourmaps

# misc packages
import sklearn.preprocessing as pre  # for data normalisation
from sklearn.metrics import pairwise_distances # fast distance matrix calculation
from inpoly import inpoly2  # for fast inpolygon checks
import datetime # for date-time data types
import configparser # to work with warning suppression
import h5py # read/write hdf5 files

###########################
# import main local package
import SPOTSAR_main as sm
from SPOTSAR_main.Post_processing.MKA_data import MKA_data

## 2: define/load parameters
################ Define user INPUTS ################################################
######## please edit the values of this block only #################################
####################################################################################

# # define hillshade file
# HS_FILE = "/local-scratch/tz20896/Merapi2021/geo/TDX_Merapi_WGS84.tif"

# define lon and lat files
LON_FILE = "../DATA4_SPOTSAR_DEMO/CSK_dsc/geo/20200910.lon"
LAT_FILE = "../DATA4_SPOTSAR_DEMO/CSK_dsc/geo/20200910.lat"

# define parameter text file
PARAM_FILE = "./params.txt"

# define map region of interest
lon_lims = [110.425, 110.45]
lat_lims = [-7.555, -7.535]

# define colour range {min max} (min = -max)
vmax = 3  # range of colourscale in meters

# define file names for data, lon and lat
DIRECTORY_PATH = "../DATA4_SPOTSAR_DEMO/CSK_dsc/DISP_TXT/"
# define path to ccp and ccs files
DIRECTORY_PATH_CCS = "../DATA4_SPOTSAR_DEMO/CSK_dsc/CCP_CCS/"

# define regex to find files in paths defined above
CSK_off_regex = r"c[0-9]+_c[0-9]+_disp_[0-9]+_[0-9]+.txt"
CSK_ccs_regex = r"c[0-9]+_c[0-9]+_ccs_[0-9]+_[0-9]"

# filtering params
med_filt_radius = 7
cut_off_med = 0.9
MKA_indices = [0,1,2]

# define output folder for #pairname.h5 file
H5_FOLDER = '../DATA4_SPOTSAR_DEMO/CSK_dsc/h5_files/'

###########################################################
############## end of editing box #########################
###########################################################

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


### load data ###
pair_names = sm.Post_processing.get_image_pairs(
    DIRECTORY_PATH, CSK_off_regex, 19
)
print(pair_names)

pair_names_ccs = sm.Post_processing.get_image_pairs(
    DIRECTORY_PATH_CCS, CSK_ccs_regex, 19
)
print(pair_names_ccs)

# # open hill shade file with rasterio
# DEM_HS = rio.open(HS_FILE)
# SHADING = DEM_HS.read(1, masked=True)  # rasterio bands are indexed from 1

# # extract DEM extent
# DEM_EXTENT = [
#     DEM_HS.bounds.left,
#     DEM_HS.bounds.right,
#     DEM_HS.bounds.bottom,
#     DEM_HS.bounds.top,
# ]


## 3-7: functional part
#######################################################################

### load data into memory
for pair_name in pair_names:

    ### 3: load data
    # print progress
    print(f'Running pair: {pair_name}')

    # find files
    files = os.listdir(DIRECTORY_PATH)
    files_ccs = os.listdir(DIRECTORY_PATH_CCS)
    print("number of files:", np.size(files))

    # get files that match pair name
    pair_files = [file for file in files if file[:19]==pair_name]
    pair_files_ccs = [file for file in files_ccs if file[:23]==pair_name+'_ccs']

    # get range window size to sort data files
    r_win = []
    for pair_file in pair_files:
        r_win.append(int(pair_file.split('_')[-2]))
    sort_idx = np.argsort(r_win)
    sorted_pair_files = [pair_files[i] for i in sort_idx]

    r_win_ccs = []
    for pair_file_ccs in pair_files_ccs:
        r_win_ccs.append(int(pair_file_ccs.split('_')[-2]))
    sort_idx_ccs = np.argsort(r_win_ccs)
    sorted_pair_files_ccs = [pair_files_ccs[i] for i in sort_idx_ccs]

    ### 4: add data to single-kernel and Multi-kernel classes
    # add data to stack
    datastack = sm.Post_processing.MultiKernel(DIRECTORY_PATH,
                                                sorted_pair_files,
                                                DIRECTORY_PATH_CCS,
                                                sorted_pair_files_ccs,
                                                LAT_FILE,
                                                LON_FILE,
                                                HEADING,
                                                MEAN_INC,
                                                LINES_CCS,
                                                WIDTH_CCS)

    # We need to assign some data not stored in the disp.txt files.
    datastack.get_params_from_file_name()
    datastack.get_latlon_from_file(WIDTH)
    datastack.add_lat_lon_to_data(R_START,A_START)
    datastack.crop_stack_ccs(R_STEP,A_STEP)
    # the object datastack now has several attributes associated with the whole dataset (e.g., date1, date2, heading)
    # Next we add all the offset data (disp.txt) to the stack
    stacked_data = datastack.assign_data_to_stack(R_STEP,A_STEP)


    # pre-allocate field names for hdf5 file (current max is 3 window sizes)
    name = datastack.Filenames[0][0:19]
    column_names = ['win_1_Lon_pre', 'win_1_lat_pre', 'win_1_R_off_pre', 'win_1_A_off_pre',
                    'win_2_Lon_pre', 'win_2_lat_pre', 'win_2_R_off_pre', 'win_2_A_off_pre',
                    'win_3_Lon_pre', 'win_3_lat_pre', 'win_3_R_off_pre', 'win_3_A_off_pre',
                    ]

    attr_names = ['Lon_off','Lat_off','R_off','A_off',
                  'Lon_off','Lat_off','R_off','A_off',
                  'Lon_off','Lat_off','R_off','A_off',
                  ]

    h5_file = f'../PO_SBAS_PAIRS/h5_files/{name}.h5'
    h5_file = f'{H5_FOLDER}{name}.h5'


    column_names_post = ['win_1_Lon_post', 'win_1_lat_post', 'win_1_R_off_post', 'win_1_A_off_post',
                        'win_2_Lon_post', 'win_2_lat_post', 'win_2_R_off_post', 'win_2_A_off_post',
                        'win_3_Lon_post', 'win_3_lat_post', 'win_3_R_off_post', 'win_3_A_off_post',
                        ]

    ### 5: filter outliers using median filter
    # print progress
    print(f'Perform Median filtering on pair: {pair_name}')

    # run outlier filtering and MKA on multi-kernel image pair 
    for i, obj in enumerate(datastack.Stack):
        print('do med filt',med_filt_radius)
        f = h5py.File(h5_file,'a')
        R_off_med_diff, A_off_med_diff, mag_off_med_diff = obj.run_med_filt(med_filt_radius)
        obj.to_hdf5(h5_file,[f'Mag_off_med_diff_{med_filt_radius}_vec',
                                f'Mag_off_med_diff_{med_filt_radius}'])
        obj.rem_outliers_median(7,cut_off_med)
        obj.reset_vecs()

        f = h5py.File(h5_file,'a')
        f.create_dataset(column_names_post[0 + i*4], data = getattr(obj,attr_names[0 + i*4]))
        f.create_dataset(column_names_post[1 + i*4], data = getattr(obj,attr_names[1 + i*4]))
        f.create_dataset(column_names_post[2 + i*4], data = getattr(obj,attr_names[2 + i*4]))
        f.create_dataset(column_names_post[3 + i*4], data = getattr(obj,attr_names[3 + i*4]))
        f.close()


    ### 6: perfrom Multi-kernel averaging
    print(f'Perform MKA on pair: {pair_name}')
    MKA_R_off, MKA_A_off = sm.Post_processing.Run_MKA(datastack,MKA_indices,1,1,5)
    # retrieve MKA results
    MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA = sm.Post_processing.get_MKA_vec(datastack,R_STEP,A_STEP)
    MKA_data_obj = MKA_data(MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA)

    ### 7: store results in hdf5 file
    column_names_MKA = ['win_13_Lon', 'win_13_lat', 'win_13_R_off', 'win_13_A_off']
    attr_names_MKA = ['Lon_off_MKA','Lat_off_MKA','MKA_R_off','MKA_A_off']

    f = h5py.File(h5_file,'a')
    f.create_dataset(column_names_MKA[0], data = getattr(datastack,attr_names_MKA[0]))
    f.create_dataset(column_names_MKA[1], data = getattr(datastack,attr_names_MKA[1]))
    f.create_dataset(column_names_MKA[2], data = getattr(datastack,attr_names_MKA[2]))
    f.create_dataset(column_names_MKA[3], data = getattr(datastack,attr_names_MKA[3]))
    f.close()



print('Process finished.')


