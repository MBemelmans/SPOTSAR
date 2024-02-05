import pandas as pd
import numpy as np
from inpoly import inpoly2
from shapely.geometry import Polygon
from shapely.geometry.point import Point
import rasterio as rio
from sklearn import linear_model

import json
from shapely.geometry import Point, LineString, mapping
from functools import partial
from shapely.ops import transform


from .singlekernel import SingleKernel
from .geodetic2enu import geodetic2enu
from .query_point import query_point

class MultiKernel:

    def __init__(self,file_dir,filenames,file_dir_ccs,filenames_ccs,lat_file,lon_file,heading,mean_inc,lines_ccs,width_ccs):
        """
        Object that contains multi kernel stack to prepare for multi-kernel averaging

        Args:
            file_dir (str): directory containing offset files used for the stack
            filenames (list/array-like): list of filenames (str) of the offset data
            file_dir_ccs (str): directory containing CCS files used for the stack
            filenames_ccs (list/array-like): list of filenames (str) of the CCS data 
            lat_file (str): path to latitude file (.lat)
            lon_file (str): path to longitude file (.lon)
            heading (float): heading of satellite acquisitions
            mean_inc (float): mean incidence angle of satellite acquisitions 
            lines_ccs (int): number of lines in CCS data from CCS files
            width_ccs (int): width of CCS data in CCS files
        """
        self.Filenames = filenames
        self.Filenames_ccs = filenames_ccs
        self.Lat_file = lat_file
        self.Lon_file = lon_file
        self.Heading = heading
        self.Mean_inc = mean_inc

        #intitialise Stack as empty list 
        self.Stack = []

        self.Data = [pd.read_csv(file_dir + disp_file, header  =None, sep = '\s+') for disp_file in self.Filenames]
        self.Data_ccs = [np.fromfile(file_dir_ccs+'/'+ccs_file, dtype='>f', count=-1) for ccs_file in self.Filenames_ccs]
        self.Ccs_maps = [np.transpose(np.reshape(d,(lines_ccs,width_ccs))) for d in self.Data_ccs]


    def get_params_from_file_name(self):
        """
            Extract important parameters from file names
        """
        self.Date1     = []
        self.Date2     = []
        self.R_win     = []
        self.A_win     = []
        for disp_file in self.Filenames:
            # split files with '_' as delimiter
            strings = disp_file.split('_')
            # extract dates (remove first character)
            self.Date1.append(strings[0][1:])
            self.Date2.append(strings[1][1:])
            # extract windown size parameters
            self.R_win.append(int(strings[3]))
            self.A_win.append(int(strings[4][0:-4]))
        
    def get_latlon_from_file(self,width):
        """
            extracts latitude and longitude of data from .lat and .lon file
            result is stored in np array with size width,n_lines
            n_lines is calculated from width and size of the data.
        """
        # get latitude and longitude data from file
        lon_vec = np.fromfile(self.Lon_file, dtype='>f', count=-1)
        lat_vec = np.fromfile(self.Lat_file, dtype='>f', count=-1)
        # set 0,0 coordinates to nan
        lon_vec[lon_vec == 0] = np.nan
        lat_vec[lat_vec == 0] = np.nan
        # get number of lines in lat lon files
        lines_ll = lon_vec.shape[0]/width
        # reshape tomatrix for index referencing
        LON = np.reshape(lon_vec,[int(lines_ll),width])
        LAT = np.reshape(lat_vec,[int(lines_ll),width])

        # assign to stack object
        self.Lon_vec = lon_vec
        self.Lat_vec = lat_vec
        self.Lon = LON
        self.Lat = LAT

        return LAT, LON
    

    def add_lat_lon_to_data(self,r_start,a_start):
        for file in self.Data:
            file[9]  = self.Lat[file[1]+a_start-1,file[0]+r_start-1]
            file[10] = self.Lon[file[1]+a_start-1,file[0]+r_start-1]
    
    
    def crop_stack_ccs(self,r_step,a_step):
        """
            crops a stack of measurements to the common grid (trims the edges)
            makes sure each observation has same number of points
            appends column and row index to data
            appends ccs to data
        """
        # initialise pixel coord limits
        start_rng = []
        end_rng   = []
        start_azi = []
        end_azi   = []

        # collect starting and ending measurement
        for d in self.Data:
            start_rng.append(d.iloc[0,0])
            end_rng.append(d.iloc[-1,0])
            start_azi.append(d.iloc[0,1])
            end_azi.append(d.iloc[-1,1])

        # get inner limits
        rng_min = np.max(start_rng)
        rng_max = np.min(end_rng)
        azi_min = np.max(start_azi)
        azi_max = np.min(end_azi)
        self.Limits = (rng_min,rng_max,azi_min,azi_max)

        # crop_ccs maps
        common_mask_data_ccs = []
        for d_ccs in zip(self.Ccs_maps):
            d_crop_0 = d_ccs[0][int((rng_min/r_step)):int((rng_max/r_step+1)),int((azi_min/a_step)):int((azi_max/a_step)+1)]
            common_mask_data_ccs.append(d_crop_0)

        # make new list of data that has common bounds 
        common_mask_data = []
        for d in self.Data:
            d_crop = d.loc[(d[0] >= rng_min) & (d[1] >= azi_min) & (d[0] <= rng_max) & (d[1] <= azi_max)].reset_index(drop=True)
            common_mask_data.append(d_crop)
        
        # assign data lists to Stack object
        self.Mask_data_ccs = common_mask_data_ccs
        self.Mask_data = common_mask_data

        for file,ccs_file in zip(self.Mask_data,self.Ccs_maps):
            file[11] = (file[0]-file[0][0])/r_step
            file[12] = (file[1]-file[1][0])/a_step
            file[11] = file[11].astype('int64')
            file[12] = file[12].astype('int64')
            file[13] = ccs_file[file[11],file[12]]
        
        return self.Mask_data, self.Mask_data_ccs, self.Limits

    def assign_data_to_stack(self,r_step,a_step):
        """
        collects data from files and filenames and loads them as 
        SingleKernel objects in list.

        Args:
            r_step (int): range step size in original radar coordinates 
            a_step (int): azimuth step size in original radar coordinates 

        Returns:
            self.Stack: list of SingleKernel objects that are cropped 
                        to the shared data extend and have nans removed. 
        """
        # define grid of range and azimuth pixel where offset is measured (+1 to go from number of intervals to number of observations)
        rng = np.linspace(self.Limits[0],self.Limits[1],int((self.Limits[1]-self.Limits[0])/r_step)+1)
        azi = np.linspace(self.Limits[2],self.Limits[3],int((self.Limits[3]-self.Limits[2])/a_step)+1)
        RNG, AZI = np.meshgrid(rng,azi)


        # find number of range estimates
        for d, file, date_1, date_2, r__win, a__win, ccs_map in zip(self.Mask_data, self.Filenames, self.Date1, self.Date2, self.R_win, self.A_win,self.Mask_data_ccs):
            # initiate arrays
            r_off   = np.full(np.shape(RNG)[::-1], np.nan)
            a_off   = np.full(np.shape(RNG)[::-1], np.nan)    
            ccp_off = np.full(np.shape(RNG)[::-1], np.nan)
            lat_off = np.full(np.shape(RNG)[::-1], np.nan)
            lon_off = np.full(np.shape(RNG)[::-1], np.nan)
            r_idx   = np.full(np.shape(RNG)[::-1], np.nan)
            a_idx   = np.full(np.shape(RNG)[::-1], np.nan)
            ccs_off = np.full(np.shape(RNG)[::-1], np.nan)
            # fill arrays form indexes 
            r_off[d[11],d[12]] = d[7]
            a_off[d[11],d[12]] = d[8]
            ccp_off[d[11],d[12]] = d[6]
            lat_off[d[11],d[12]] = d[9]
            lon_off[d[11],d[12]] = d[10]
            r_idx[d[11],d[12]] = d[0]
            a_idx[d[11],d[12]] = d[1]
            # ccs_off[d[11],d[12]] = d[13]
            ccs_off = ccs_map

            # make object
            offset_data = SingleKernel(file,[date_1,date_2],[r__win,a__win],self.Heading,[r_idx,a_idx,r_off,a_off,ccp_off,lat_off,lon_off,ccs_off])
            # do pre-stacking processing
            offset_data.calc_SNR()
            offset_data.calc_Mag()
            offset_data.calc_phase()
            offset_data.rotate_with_heading()
            offset_data.mask_nan_data()
            offset_data.rem_nans()
            
            self.Stack.append(offset_data)

        return self.Stack
    
    def Run_MKA(self,indeces=[],window_size=1,comp_lim=0.5):
        # """
        # Run Multi-kernel averaging where user can define seleced indices from the stack, 
        # desired window size, and a completion factor as a high pass filter

        # Args:
        #     indices (list, optional): indices of slices from datastack used for MKA. Defaults to [], use all data.
        #     window_size (int, optional): window dimension for MKA, odd numbers 
        #                                  prefered because of pixel centering. 
        #                                  Defaults to 1.
        #     comp_lim (float, optional): completion limit between [0.0, 1.0]
        #                                 Only take data for MKA if more than 
        #                                 comp_lim of the stack is not nan. 
        #                                 Defaults to 0.5.

        # Returns:
        #     avg_map: Multi-kernel Average map
        # """
        # get stack data
        if indeces==[]:
            stack_R = [obj.R_off for obj in self.Stack]
            stack_A = [obj.A_off for obj in self.Stack]
            stack_ccp = [obj.Ccp_off for obj in self.Stack]
            stack_ccs = [obj.Ccs_off for obj in self.Stack]
        else:
            substack = [self.Stack[i] for i in indeces]
            stack_R = np.stack([obj.R_off for obj in substack],axis=0)
            stack_A = np.stack([obj.A_off for obj in substack],axis=0)
            stack_ccp = np.stack([obj.Ccp_off for obj in substack],axis=0)
            stack_ccs = np.stack([obj.Ccs_off for obj in substack],axis=0)

        # create list of maps to make 
        avg_maps = []

        for stack in [stack_R,stack_A]:
            # set window size according to stack dimensions
            window_shape = (stack.shape[0], window_size, window_size)
            print(np.shape(window_shape))
            # use np.lib.stride_tricks.sliding_window_view to devided data into windows
            # 1.2xfaster than sklearn view_as_windows
            win_data = np.lib.stride_tricks.sliding_window_view(stack, window_shape)[0]

            # remove data that is nan for too many different window sizes
            nan_frac = np.sum(np.isnan(win_data), axis=2) / (window_size ** 2)
            nan_frac = nan_frac/np.shape(win_data)[2]
            nan_frac[nan_frac > comp_lim] = np.nan
            nan_frac[nan_frac <= comp_lim] = 1
            win_data = np.multiply(win_data, nan_frac[..., np.newaxis])

            # define shape of multi-kernel averaged map (same as input data), filled with nan
            Avg_map = np.full(stack.shape[1:], np.nan)

            # per window, go take 95% confidence interval data and take average (mean)
            for win_i in range(win_data.shape[0]):
                if win_i % 50 == 0:
                    print('win_i', win_i)
                for win_j in range(win_data.shape[1]):
                    # extract relevant window
                    win = win_data[win_i, win_j]
                    # calculate 95 % confidence interval
                    percentiles = np.nanpercentile(win, [2.5, 97.5])
                    # mask data outside 95% confidence interval with nan
                    mask = (win < percentiles[0]) | (win > percentiles[1])
                    win[mask] = np.nan
                    # calculate mean of window (offset by floor(window_size/2) because of border)
                    offset = window_size // 2
                    Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)
            avg_maps.append(Avg_map)
        self.MKA_R_off = avg_maps[0]
        self.MKA_A_off = avg_maps[1]
        # stack_obj.MKA_Ccp_off = avg_maps[2]
        # stack_obj.MKA_Ccs_off = avg_maps[3]

        return self.MKA_R_off, self.MKA_A_off
    

    def Run_RSS(self,indeces=[],window_size=5,deramp=True):
        # """
        # Calculate residual sum of squares. user can specify window size and can turn off deramping if desired

        # Args:
        #     indices (list, optional): indices of slices from datastack used for MKA. Defaults to [], use all data.
        #     window_size (int, optional): window dimension for MKA, odd numbers 
        #                                  prefered because of pixel centering. 
        #                                  Defaults to 5.
        #     deramp (bool, optional): flag for deramping data in map coordinates 
        #                              to allow for better estimates in gradual displacement 
        #                              fields. deramping in map coordinates does not do local 
        #                              transformation to ortholinear projection so there may 
        #                              be inaccuracies. 
        # Returns:
        #     RSS_list: list of resisual sum of squares
        # """
        # get stack data
        if indeces==[]:
            stack_R = [obj.R_off for obj in self.Stack]
            stack_A = [obj.A_off for obj in self.Stack]
            stack_lon = [getattr(obj,'Lon_off') for obj in self.Stack]
            stack_lat = [getattr(obj,'Lat_off') for obj in self.Stack]

        else:
            substack = [self.Stack[i] for i in indeces]
            stack_R = np.stack([obj.R_off for obj in substack],axis=0)
            stack_A = np.stack([obj.A_off for obj in substack],axis=0)
            stack_lons = np.stack([getattr(obj,'Lon_off') for obj in substack])
            stack_lats = np.stack([getattr(obj,'Lat_off') for obj in substack])

        # create list of rss values
        rss_list = []

        for stack_r,stack_a,stack_lon,stack_lat in zip(stack_R,stack_A,stack_lons,stack_lats):
            # set window size according to stack dimensions
            window_shape = (stack_r.shape[0], window_size, window_size)
            print(np.shape(window_shape))
            # use np.lib.stride_tricks.sliding_window_view to devided data into windows
            # 1.2xfaster than sklearn view_as_windows
            win_data_r = np.lib.stride_tricks.sliding_window_view(stack_r, window_shape)[0]
            win_data_a = np.lib.stride_tricks.sliding_window_view(stack_a, window_shape)[0]

            win_data_lon = np.lib.stride_tricks.sliding_window_view(stack_lon, window_shape)[0]
            win_data_lat = np.lib.stride_tricks.sliding_window_view(stack_lat, window_shape)[0]
            
            # define shape of multi-kernel averaged map (same as input data), filled with nan
            Avg_map_r = np.full(stack_r.shape[1:], np.nan)
            Avg_map_a = np.full(stack_a.shape[1:], np.nan)



            # per window, go take 95% confidence interval data and take average (mean)
            for win_i in range(win_data_r.shape[0]):
                if win_i % 50 == 0:
                    print('win_i', win_i)
                for win_j in range(win_data_r.shape[1]):
                    # extract relevant window
                    win_r = win_data_r[win_i, win_j]
                    win_a = win_data_a[win_i, win_j]
                    
                    lon_win = win_data_lon[win_i,win_j]
                    lat_win = win_data_lat[win_i,win_j]
                    # calculate 95 % confidence interval
                    percentiles_r = np.nanpercentile(win_r, [2.5, 97.5])
                    percentiles_a = np.nanpercentile(win_a, [2.5, 97.5])
                    # mask data outside 95% confidence interval with nan
                    mask_r = (win_r < percentiles_r[0]) | (win_r > percentiles_r[1])
                    mask_a = (win_a < percentiles_a[0]) | (win_a > percentiles_a[1])
                    mask = (mask_r | mask_a)
                    win_r[mask] = np.nan
                    win_a[mask] = np.nan
                    lon_win[mask] = np.nan
                    lat_win[mask] = np.nan
                    
                    #deramp
                    if deramp:
                        X_data = np.transpose(np.stack((lon_win.flatten(),lat_win.flatten())))
                        Y_data_r = win_r.flatten()
                        reg = linear_model.LinearRegression().fit(X_data, Y_data_r)
                        deramped_r =win_r.flatten() - lon_win.flatten() * reg.coef_[0] - lat_win.flatten() * reg.coef_[1]

                        Y_data_a = win_a.flatten()
                        reg = linear_model.LinearRegression().fit(X_data, Y_data_a)
                        deramped_a =win_a.flatten() - lon_win.flatten() * reg.coef_[0] - lat_win.flatten() * reg.coef_[1]
                    else:
                        deramped_r = win_r.flatten()
                        deramped_a = win_a.flatten()

                    # calculate mean of window (offset by floor(window_size/2) because of border)
                    offset = window_size // 2
                    Avg_map_r[win_i + offset, win_j + offset] = np.nanstd(deramped_r)**2
                    Avg_map_a[win_i + offset, win_j + offset] = np.nanstd(deramped_a)**2
                    
                    rss = (np.sum(Avg_map_r),np.sum(Avg_map_a))
            rss_list.append(rss)
        self.Rss_list = rss_list

        return self.Rss_list
    

    def query_point_stack(self,data_attr_name,q_lats,q_lons,r,indeces=[]):
        """calculatess mean, median, standard deviation and 95% confidence interval 
        for attribute data within r radius of query points

        Args:
            data_attr (_type_): attribute value of all points
            q_lats (_type_): list of query point latitudes
            q_lons (_type_): list of query point longitudes
            r (_type_): search radius in meters
            indeces (list, optional): list of stack indeces to process
        """

        ##
        # function transforms query point (lon,lat)WGS84 into 
        # local azimuthal projection (rect-linear with minimum local distortion)
        # then applies a buffer of desired radius in meters to that point 
        # and makes a n-gon polygonal apprixomation of a circle 

        if indeces==[]:
            substack = self.Stack
        else:
            substack = [self.Stack[i] for i in indeces]

        # pre-define stat-list for appending
        stats_list = []

        # loop over window_sizes in subtrack
        for obj in substack:
            # get lat lon and attribute data
            lons = getattr(obj,'Lon_off_vec')
            lats = getattr(obj,'Lat_off_vec')
            data_attr = getattr(obj,data_attr_name)

            q_mean, q_median, q_std, q_95, coordinate_circles = query_point(lats,
                                                                            lons,
                                                                            data_attr,
                                                                            q_lats,
                                                                            q_lons,
                                                                            r)
            stats_list.append([getattr(obj,'R_win'),getattr(obj,'A_win'),q_mean, q_median, q_std, q_95])
        return stats_list, coordinate_circles

    def query_point_MKA(self,data_attr_name,q_lats,q_lons,r):
        """calculatess mean, median, standard deviation and 95% confidence interval 
        for attribute data within r radius of query points

        Args:
            data_attr (_type_): attribute value of all points
            q_lats (_type_): list of query point latitudes
            q_lons (_type_): list of query point longitudes
            r (_type_): search radius in meters
            indeces (list, optional): list of stack indeces to process
        """

        ##
        # function transforms query point (lon,lat)WGS84 into 
        # local azimuthal projection (rect-linear with minimum local distortion)
        # then applies a buffer of desired radius in meters to that point 
        # and makes a n-gon polygonal apprixomation of a circle 
        nan_mask = np.isnan(self.MKA_R_off).flatten()
        p_slice = self.Stack[1]
        lons = getattr(p_slice,'Lon_off').flatten()
        lats = getattr(p_slice,'Lat_off').flatten()
        lons = getattr(p_slice,'Lon_off').flatten()
        lats = getattr(p_slice,'Lat_off').flatten()
        # lons = self.Lon.flatten()
        # lats = self.Lat.flatten()
        data_attr = getattr(self,data_attr_name).flatten()

        q_mean, q_median, q_std, q_95, coordinate_circles = query_point(lats,
                                                                        lons,
                                                                        data_attr,
                                                                        q_lats,
                                                                        q_lons,
                                                                        r)

        return [q_mean, q_median, q_std, q_95], coordinate_circles

    
    def outlier_detection_HDBSCAN_stack(self,N_overlap,min_samples_fact,hard_lim,h5_file):
        HDBSCAN_list = []
        GLOSH_list = []

        for obj in self.Stack:
            overlap = np.ceil((obj.R_win/R_STEP) * (obj.A_win/A_STEP))
            print(f'current window size: {obj.R_win}, {obj.A_win}, overlap: {overlap}')
            hard_limit = hard_lim
            min_cluster_size = np.max([int(np.round(N_overlap*overlap)),hard_limit])
            min_samples = np.max([1,int(np.round(min_cluster_size*min_samples_fact))])
            print(f'min cluster size: {min_cluster_size}')
            print(f'min samples: {min_samples}')
            # normalize data 
            obj.prep_DBSCAN(1,1,100)
            # perform PCA (does not do much)
            obj.run_PCA(4)
            # run HDBSCAN + GLOSH
            f = h5py.File(h5_file,'a')
            if f'HDBSCAN_labels_{int(min_cluster_size)}_{int(min_samples)}_vec' not in f:
                f.close()
                HDBSCAN_labels, GLOSH_probabilities, HDBSCAN_probabilities = obj.run_HDBSCAN(int(min_cluster_size),int(min_samples),False,0.0)
                HDBSCAN_list.append( HDBSCAN_probabilities)
                GLOSH_list.append(GLOSH_probabilities)
                obj.to_hdf5(h5_file,[f'HDBSCAN_labels_{int(min_cluster_size)}_{int(min_samples)}_vec',
                                    f'HDBSCAN_outlier_scores_{int(min_cluster_size)}_{int(min_samples)}_vec',
                                    f'HDBSCAN_probabilities_{int(min_cluster_size)}_{int(min_samples)}_vec',
                                    f'HDBSCAN_labels_{int(min_cluster_size)}_{int(min_samples)}',
                                    f'HDBSCAN_outlier_scores_{int(min_cluster_size)}_{int(min_samples)}',
                                    f'HDBSCAN_probabilities_{int(min_cluster_size)}_{int(min_samples)}'])
        return HDBSCAN_list, GLOSH_list

    def outlier_detection_LOF_stack(self,N_overlap,hard_lim,h5_file):
        LOF_list = []
        for obj in self.Stack:
            print(f'current window size: {obj.R_win}, {obj.A_win}')
            # get overlap
            overlap = np.ceil((obj.R_win/R_STEP) * (obj.A_win/A_STEP))
            hard_limit = hard_lim
            min_cluster_size = np.max([int(N_overlap*overlap),hard_limit])
            print(f'knn: {min_cluster_size}')
            # normalize data 
            obj.prep_DBSCAN(1,1,100)
            # perform PCA (does not do much)
            obj.run_PCA(4)
            # run LOF
            f = h5py.File(h5_file,'a')
            if f'LOF_labels_{int(min_cluster_size)}_vec' not in f:
                f.close()
                LOF_labels, LOF_negative_score = obj.run_LOF(n_neighbors=int(min_cluster_size),algorithm='auto',leaf_size=30,contamination='auto')
                
                obj.to_hdf5(h5_file,[f'LOF_labels_{int(min_cluster_size)}_vec',
                                    f'LOF_outlier_score_{int(min_cluster_size)}_vec',
                                    f'LOF_labels_{int(min_cluster_size)}',
                                    f'LOF_outlier_scores_{int(min_cluster_size)}'])
                LOF_list.append(LOF_negative_score)
        return LOF_list

    def outlier_detection_median_stack(self,filt_rad,h5_file):
        Median_list = []
        for obj in self.Stack:
            print(f'current window size: {obj.R_win}, {obj.A_win}')
            # run Med filt
            f = h5py.File(h5_file,'a')
            if f'Mag_off_med_diff_{filt_rad}_vec' not in f:
                f.close()
                R_off_med_diff, A_off_med_diff, mag_off_med_diff = obj.run_med_filt(filt_rad)
                obj.to_hdf5(h5_file,[f'Mag_off_med_diff_{filt_rad}_vec',
                                    f'Mag_off_med_diff_{filt_rad}'])
                Median_list.append(mag_off_med_diff)
        return Median_list