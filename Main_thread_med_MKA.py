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

import h5py

###########################
# import main local package
import SPOTSAR_main as sm


### define constants

################ Define user INPUTS #######################
######## please edit the values of this block only ########
###########################################################

# define hillshade file
HS_FILE = "/local-scratch/tz20896/Merapi2021/geo/TDX_Merapi_WGS84.tif"

# define lon and lat files
LON_FILE = "/local-scratch/tz20896/Merapi2021/CSK/dsc1/geo2/20200910.lon"
LAT_FILE = "/local-scratch/tz20896/Merapi2021/CSK/dsc1/geo2/20200910.lat"

# define parameter text file
PARAM_FILE = "./params.txt"

# define map region of interest
lon_lims = [110.425, 110.45]
lat_lims = [-7.555, -7.535]

# define colour range {min max} (min = -max)
vmax = 3  # range of colourscale in meters

# define file names for data, lon and lat
DIRECTORY_PATH = "../PO_SBAS_PAIRS/DISP_TXT/"
# define path to ccp and ccs files
DIRECTORY_PATH_CCS = "../PO_SBAS_PAIRS/CCP_CCS/"




### load data ###
pair_names = sm.Post_processing.get_image_pairs(
    DIRECTORY_PATH, r"c[0-9]+_c[0-9]+_disp_[0-9]+_[0-9]+.txt", 19
)
print(pair_names)

pair_names_ccs = sm.Post_processing.get_image_pairs(
    DIRECTORY_PATH_CCS, r"c[0-9]+_c[0-9]+_ccs_[0-9]+_[0-9]", 19
)
print(pair_names_ccs)

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


# filtering params
med_filt_radius = 7
cut_off_med = 0.9
MKA_indices = [0,1,2]

### load data into memory
for pair_name in pair_names:
    # print progress
    print(f'Running pair: {pair_name}')

    # find files
    files = os.listdir(DIRECTORY_PATH)
    files_ccs = os.listdir(DIRECTORY_PATH_CCS)
    print("number of files:", np.size(files))

    # get files that match pair name
    pair_files = [file for file in files if file[:19]==pair_name]
    pair_files_ccs = [file for file in files_ccs if file[:23]==pair_name+'_ccs']

    # get range window to sort data files
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
    # if os.path.exists(h5_file):
    #     print(f'skipping {h5_file}, file exists')
    #     continue
    # else:
    #     for i, obj in enumerate(datastack.Stack):
    #         print(f'creating {h5_file}')
    #         f = h5py.File(h5_file,'a')
    #         f.create_dataset(column_names[0 + i*4], data = getattr(obj,attr_names[0 + i*4]))
    #         f.create_dataset(column_names[1 + i*4], data = getattr(obj,attr_names[1 + i*4]))
    #         f.create_dataset(column_names[2 + i*4], data = getattr(obj,attr_names[2 + i*4]))
    #         f.create_dataset(column_names[3 + i*4], data = getattr(obj,attr_names[3 + i*4]))
    #         f.close()

    column_names_post = ['win_1_Lon_post', 'win_1_lat_post', 'win_1_R_off_post', 'win_1_A_off_post',
                        'win_2_Lon_post', 'win_2_lat_post', 'win_2_R_off_post', 'win_2_A_off_post',
                        'win_3_Lon_post', 'win_3_lat_post', 'win_3_R_off_post', 'win_3_A_off_post',
                        ]

    # print progress
    print(f'Perform Median filtering on pair: {pair_name}')


    ### old code to skip one specific file
    # if h5_file == '../PO_SBAS_PAIRS/h5_files/c20200910_c20200919.h5':
    #     a = 1
    # else:

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
    print(f'Perform MKA on pair: {pair_name}')
    MKA_R_off, MKA_A_off = sm.Post_processing.Run_MKA(datastack,MKA_indices,1,1,5)
    # retrieve MKA results
    MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA = sm.Post_processing.get_MKA_vec(datastack)
    MKA_data_obj = sm.Post_processing.MKA_data(MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA)

    # store results in hdf5 file
    column_names_MKA = ['win_13_Lon', 'win_13_lat', 'win_13_R_off', 'win_13_A_off']
    attr_names_MKA = ['Lon_off_MKA','Lat_off_MKA','MKA_R_off','MKA_A_off']

    f = h5py.File(h5_file,'a')
    f.create_dataset(column_names_MKA[0], data = getattr(datastack,attr_names_MKA[0]))
    f.create_dataset(column_names_MKA[1], data = getattr(datastack,attr_names_MKA[1]))
    f.create_dataset(column_names_MKA[2], data = getattr(datastack,attr_names_MKA[2]))
    f.create_dataset(column_names_MKA[3], data = getattr(datastack,attr_names_MKA[3]))
    f.close()



print('Process finished.')



### useful functions ###

# def get_image_pairs(folder_path, regex_str, length):
#     # Get a list of all files in the folder
#     files = os.listdir(folder_path)
#     print("number of files:", np.size(files))

#     # Define the regular expression pattern
#     pattern = re.compile(regex_str)

#     # Filter and sort files based on the first 11 characters
#     sorted_files = sorted(
#         [file for file in files if pattern.match(file)], key=lambda x: x[:length]
#     )
#     print("number of files mathing pattern:", np.size(sorted_files))

#     unique_files = []
#     for file in sorted_files:
#         if file[:length] not in unique_files:
#             unique_files.append(file[:length])

#     print("number of unique image pairs:", np.size(unique_files))
#     return unique_files



# def Run_MKA(q_obj,indeces=[],window_size=1,comp_lim=0.5,CI_lim=5):
#         """
#         Run Multi-kernel averaging where user can define seleced indices from the stack, 
#         desired window size, and a completion factor as a high pass filter

#         Input:
#             q_obj (multi_kernel class objects): multi-kernel (multi-window) data object for the image pair in question.

#         Args:
#             indices (list, optional): indices of slices from datastack used for MKA. Defaults to [], use all data.
#             window_size (int, optional): window dimension for MKA, odd numbers 
#                                          prefered because of pixel centering. 
#                                          Defaults to 1.
#             comp_lim (float, optional): completion limit between [0.0, 1.0]
#                                         Only take data for MKA if more than 
#                                         comp_lim of the stack is not nan. 
#                                         Defaults to 0.5.

#         Returns:
#             avg_map: Multi-kernel Average map
#         """
#         # get stack data
#         if indeces==[]:
#             stack_R = [obj.R_off for obj in q_obj.Stack]
#             stack_A = [obj.A_off for obj in q_obj.Stack]
#             stack_ccp = [obj.Ccp_off for obj in q_obj.Stack]
#             stack_ccs = [obj.Ccs_off for obj in q_obj.Stack]
#         else:
#             substack = [q_obj.Stack[i] for i in indeces]
#             stack_R = np.stack([obj.R_off for obj in substack],axis=0)
#             stack_A = np.stack([obj.A_off for obj in substack],axis=0)
#             stack_ccp = np.stack([obj.Ccp_off for obj in substack],axis=0)
#             stack_ccs = np.stack([obj.Ccs_off for obj in substack],axis=0)

#         # create list of maps to make 
#         avg_maps = []
#         offset = window_size // 2

#         for stack in [stack_R,stack_A]:
#             # set window size according to stack dimensions
#             window_shape = (stack.shape[0], window_size, window_size)
#             print(np.shape(window_shape))
#             # define shape of multi-kernel averaged map (same as input data), filled with nan
#             Avg_map = np.full(stack.shape[1:], np.nan)
            
#             # use np.lib.stride_tricks.sliding_window_view to devided data into windows
#             # 1.2xfaster than sklearn view_as_windows
#             win_data = np.lib.stride_tricks.sliding_window_view(stack, window_shape)[0]



#             # remove data that is nan for too many different window sizes
#             nan_frac = np.sum(np.isnan(win_data), axis=2) / (window_size ** 2)
#             nan_frac = nan_frac/np.shape(win_data)[2]
#             nan_frac[nan_frac > comp_lim] = np.nan
#             nan_frac[nan_frac <= comp_lim] = 1
#             win_data = np.multiply(win_data, nan_frac[..., np.newaxis])

#             # # define shape of multi-kernel averaged map (same as input data), filled with nan
#             Avg_map = np.full(stack.shape[1:], np.nan)

#             # per window, go take 95% confidence interval data and take average (mean)
#             for win_i in range(win_data.shape[0]):
#                 if win_i % 50 == 2:
#                     print('win_i', win_i)
#                     print('win',win.flatten(),'mean',np.nanmean(win), 'z_score',z_score.flatten())
#                 for win_j in range(win_data.shape[1]):
#                     offset = window_size // 2
#                     # extract relevant window
#                     win = win_data[win_i, win_j]
#                     # calculate 95 % confidence interval
#                     if np.sum(~np.isnan(win))==1:
#                          Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)
#                     elif CI_lim == 0:
#                          Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)
#                     else:
#                         data_std = np.nanstd(win)
#                         data_mean = np.nanmean(win)
#                         z_score = (win-data_mean)/data_std
#                         mask = np.abs(z_score) > 1 # 95 conf interval
#                         win[mask] = np.nan
#                         Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)


#             avg_maps.append(Avg_map)
#         q_obj.MKA_R_off = avg_maps[0]
#         q_obj.MKA_A_off = avg_maps[1]

#         return q_obj.MKA_R_off, q_obj.MKA_A_off


# def get_MKA_vec(obj):
#     # Lon_off = getattr(obj.Stack[2],'Lon_off')
#     # Lat_off = getattr(obj.Stack[2],'Lat_off')

#     rng = np.linspace(obj.Limits[0],obj.Limits[1],int((obj.Limits[1]-obj.Limits[0])/R_STEP)+1)
#     azi = np.linspace(obj.Limits[2],obj.Limits[3],int((obj.Limits[3]-obj.Limits[2])/A_STEP)+1)
#     RNG, AZI = np.meshgrid(rng,azi)

#     Lat_off = np.full(np.shape(RNG)[::-1], np.nan)
#     Lon_off = np.full(np.shape(RNG)[::-1], np.nan)
#     # find number of range estimates
#     for d in obj.Mask_data:
#         # fill arrays form indexes 
#         Lat_off[d[11],d[12]] = d[9]
#         Lon_off[d[11],d[12]] = d[10]
#     setattr(obj,'Lon_off_MKA',Lon_off)
#     setattr(obj,'Lat_off_MKA',Lat_off)
    
#     nan_mask = np.isnan(obj.MKA_R_off)
#     MKA_R_off_vec = obj.MKA_R_off[~nan_mask].ravel()
#     MKA_A_off_vec = obj.MKA_A_off[~nan_mask].ravel()
#     Lon_off_MKA_vec = obj.Lon_off_MKA[~nan_mask].ravel()
#     Lat_off_MKA_vec = obj.Lat_off_MKA[~nan_mask].ravel()

#     # set attributes
#     setattr(obj,'MKA_R_off_vec', MKA_R_off_vec)
#     setattr(obj,'MKA_A_off_vec', MKA_A_off_vec)
#     setattr(obj,'Lon_off_MKA_vec', Lon_off_MKA_vec)
#     setattr(obj,'Lat_off_MKA_vec', Lat_off_MKA_vec)

#     # get map data
#     MKA_R_off = obj.MKA_R_off
#     MKA_A_off = obj.MKA_A_off
#     Lon_off_MKA = obj.Lon_off_MKA
#     Lat_off_MKA = obj.Lat_off_MKA

#     return MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA


### useful classes

# class MKA_data:

#     def __init__(self,mka_R_off_vec, mka_A_off_vec, lon_off_MKA_vec, lat_off_MKA_vec, mka_R_off, mka_A_off, lon_off_MKA, lat_off_MKA):
#         self.MKA_R_off_vec = mka_R_off_vec
#         self.MKA_A_off_vec = mka_A_off_vec
#         self.Lon_off_MKA_vec = lon_off_MKA_vec
#         self.Lat_off_MKA_vec = lat_off_MKA_vec
#         self.MKA_R_off = mka_R_off
#         self.MKA_A_off = mka_A_off
#         self.Lon_off_MKA = lon_off_MKA
#         self.Lat_off_MKA = lat_off_MKA
