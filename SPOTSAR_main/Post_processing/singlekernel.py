from sklearn import preprocessing as pre
from sklearn.decomposition import PCA
import numpy as np

class SingleKernel:
    """ 
        This class is used to represent a dataset as a pd dataframe for SAR pixel offset tracking results
        ...
        Attr
        ----------
        Name  : str
            represents file name of object
        Date[1|2] : str
            Represent the dates 1 and 2 of the image pair
        R_win : int
            Represents the number of pixels in range used for the window size
        A_win : int
            Represents the number of pixels in azimuth used for the window size
        Heading : float
            Represents the flight direction of the satellite during acquisition

        R_idx : np.array
            Represents range index number for lat lon
        A_idx : np.array   
            Represtent azimuth index number for lat lon
        

        R_off : np.array
            Represents range offset as array with nans for data gaps
        A_off : np.array
            Represents azimuth offset as array with nans for data gaps
        Ccp_off : np.array
            Represents  cross-correlation peak as array for maps with nans for data gaps 
        Lat_off : np.array
            Represents latitudes of points
        Lon_off : np.array
            Represents longitude of points
        Ccs_off : np.array
            Represents cross-correlation standard deviation for maps with nans for data gaps



        Calculated Attributes:
        ----------------------

        SNR : np.array
            Signal to noise ratio defined as ccp_off/ccs_off
        Nan_mask : np;array
            Represents where data is missing
        Nan_mask2 : np.array
            Represents where data is missing or is filtered out
        X_off : np.array
            Represents offset in quasi- E-W direction
        Y_off : np.array
            Represents offset in quasi- N-S direction
        Phase : np.array
            Represents direction of displacement in degrees from north
        X_pre : np.array
            Represents column stacked data vector used for DBSCAN or HDBSCAN (not-normalised)
        X     : np.array
            Represents column stacked data vector used for DBSCAN or HDBSCAN (normalised)
        X_pca : np.array
            Represents principle components of self.X to be used in DBSCAN of HDBSCAN
        DBSCAN_labels : np.array
            Represents labels given by DBSCAN, used for outlier removal
        HDBSCAN_labels : np.array
            Represents labels given by HDBSCAN, used for outlier removal  
        HDBSCAN_outlier_scores : np.array
            Represents the likelihood a point is an outlier.
        

    """

    def __init__(self, name, dates, win_size, heading, data):
        """
        initialise class

        Args:
            name (string): filename of single kernel data
            dates (list of ints): list with 2 elements (date1, date2) in the format yyyymmdd
            win_size (list of ints): list with 2 elements (R_win, A_win) 
            heading (float): heading of satellite acquisition
            data (list of np.arrays): list of numpy arrays containing the data:
            data[0] = range index
            data[1] = azimuth index
            data[2] = range offset
            data[3] = azimuth offset
            data[4] = cross-correlation peak 
            data[5] = latitude
            data[6] = longitude
            data[7] = cross-correlation standard deviation 
        """
        self.Name = name
        self.Date1 = dates[0]
        self.Date2 = dates[1]
        self.R_win = win_size[0]
        self.A_win = win_size[1]
        self.R_idx = data[0]
        self.A_idx = data[1]
        self.R_off = data[2]
        self.A_off = data[3]
        self.Ccp_off = data[4]
        self.Lat_off = data[5]
        self.Lon_off = data[6]

        data[7][data[7]==0] = np.nan
        self.Ccs_off = data[7]
        self.Heading = heading

    def get_attr_list(self):
        """
            returns list of attribute keys of this object
        """
        return self.__dict__.keys()

    def get_dates(self):
        """
            Returns the dates as strings in 'yyyymmdd' format
        """
        return str(self.Date1), str(self.Date2)

    def get_window_size(self):
        """
            Returns the used window size as integers Range, Azimuth
        """
        return self.R_win, self.A_win
    
    def get_data(self):
        """
            Returns data as list of np.arrays    
        """
        return self.R_idx, self.A_idx, self.R_off, self.A_off, self.Ccp_off

    def get_coords(self):
        """
            Returns coordinates of data as two np.arrays. lat, lon
        """
        return self.Lat_off, self.Lon_off


    def calc_SNR(self):
        """
            Returns Cross-correlation standard deviation
        """
        self.SNR = np.divide(self.Ccp_off,self.Ccs_off)
        return self.SNR

    def calc_Mag(self):
        """
            Stores and returns magnitude of displacement in the slant-range azimuth plane
        """
        self.Mag = np.hypot(self.R_off,self.A_off)
        return self.Mag

    
    def mask_nan_data(self):
        """
            creates a common nan mask from ccp and ccs (imported from different files)
            and masks map data accordingly
        """
        arr_shape = np.shape(self.R_off)
        nan_mask = (np.isnan(self.Ccp_off) | np.isnan(self.Ccs_off) | np.isnan(self.Lat_off))
        self.A_off = np.reshape(np.where(nan_mask,np.nan,self.A_off),arr_shape)
        self.R_off = np.reshape(np.where(nan_mask,np.nan,self.R_off),arr_shape)
        self.Ccp_off = np.reshape(np.where(nan_mask,np.nan,self.Ccp_off),arr_shape)
        self.Ccs_off = np.reshape(np.where(nan_mask,np.nan,self.Ccs_off),arr_shape)
        self.Lat_off = np.reshape(np.where(nan_mask,np.nan,self.Lat_off),arr_shape)
        self.Lon_off = np.reshape(np.where(nan_mask,np.nan,self.Lon_off),arr_shape)
        self.Nan_mask = np.reshape(nan_mask,arr_shape)
        # add optional attributes
        if hasattr(self,'SNR'):
            self.SNR = np.reshape(np.where(nan_mask,np.nan,self.SNR),arr_shape)
        if hasattr(self,'Mag'):
            self.Mag = np.reshape(np.where(nan_mask,np.nan,self.Mag),arr_shape)
        if hasattr(self,'X_off'): 
            self.X_off = np.reshape(np.where(nan_mask,np.nan,self.X_off),arr_shape)
            self.Y_off = np.reshape(np.where(nan_mask,np.nan,self.Y_off),arr_shape)
        if hasattr(self,'Phase'):
            self.Phase = np.reshape(np.where(nan_mask,np.nan,self.Phase),arr_shape)
        return self.Nan_mask
    
    def rotate_with_heading(self):
        """
            calculates displacement in (quasi) E-W (x component) and (quasi) N-S (y component)
        """
        self.R_off_vec = np.ravel(self.R_off)
        self.A_off_vec = np.ravel(self.A_off)
        rot_mat = np.array([[np.cos(np.deg2rad(self.Heading)),-np.sin(np.deg2rad(self.Heading))],
                            [np.sin(np.deg2rad(self.Heading)),np.cos(np.deg2rad(self.Heading))]])

        rot_vec = np.dot(np.column_stack((self.R_off_vec.T,self.A_off_vec.T)),rot_mat)

        self.X_off_vec= rot_vec[:,0]
        self.Y_off_vec= rot_vec[:,1]
        self.Row_index, self.Col_index = np.indices(np.shape(self.R_idx)) 
        self.X_off = np.full(np.shape(self.R_off),np.nan)
        self.Y_off = np.full(np.shape(self.R_off),np.nan)
        self.X_off[np.ravel(self.Row_index),np.ravel(self.Col_index)] = self.X_off_vec
        self.Y_off[np.ravel(self.Row_index),np.ravel(self.Col_index)] = self.Y_off_vec

        return self.X_off, self.Y_off

    def calc_phase(self):
        """
            Calculates direction (phase of displacement vector)
            -np.arctan2 to go clockwise
            +90 to offset 0 deg. from x axis to y axis
            +heading to rotate vectors to north=0
        """
        self.Phase = np.degrees(-np.arctan2(self.A_off, self.R_off)) +90 + self.Heading
        self.Phase = np.where(self.Phase < 0, self.Phase + 360, self.Phase % 360)

        return self.Phase

    def rem_nans(self):
        """
            returns nan free data and gives index off data in class instance. 
        """
        self.Row_index, self.Col_index = np.indices(np.shape(self.R_idx)) 
        self.Nan_mask_vec = np.ravel(self.Nan_mask)
        self.A_off_vec = np.ravel(self.A_off)[~self.Nan_mask_vec]
        self.R_off_vec = np.ravel(self.R_off)[~self.Nan_mask_vec]
        self.A_idx_vec = np.ravel(self.A_idx)[~self.Nan_mask_vec]
        self.R_idx_vec = np.ravel(self.R_idx)[~self.Nan_mask_vec]
        self.Ccp_off_vec = np.ravel(self.Ccp_off)[~self.Nan_mask_vec]
        self.Ccs_off_vec = np.ravel(self.Ccs_off)[~self.Nan_mask_vec]
        self.Lon_off_vec = np.ravel(self.Lon_off)[~self.Nan_mask_vec]
        self.Lat_off_vec = np.ravel(self.Lat_off)[~self.Nan_mask_vec]
        self.Row_index_vec = np.ravel(self.Row_index)[~self.Nan_mask_vec]
        self.Col_index_vec = np.ravel(self.Col_index)[~self.Nan_mask_vec]
        # add optional attributes
        if hasattr(self,'SNR'):
            self.SNR_vec = np.ravel(self.SNR)[~self.Nan_mask_vec]
        if hasattr(self,'Mag'):
            self.Mag_vec = np.ravel(self.Mag)[~self.Nan_mask_vec]
        if hasattr(self,'X_off'): 
            self.X_off_vec = np.ravel(self.X_off)[~self.Nan_mask_vec]
            self.Y_off_vec = np.ravel(self.Y_off)[~self.Nan_mask_vec]
        if hasattr(self,'Phase'):
            self.Phase_vec = np.ravel(self.Phase)[~self.Nan_mask_vec]

    def get_Row_col_idx(self):
        """retrieve row and column index of 2d array data

        Returns:
            Row_index: index of rows (axis 0)
            Col_index: index of cols (axis 1)
        """
        return self.Row_index, self.Col_index

    def get_Row_Col_vec(self):
        """retrieve row and column index of 2d array data as vectors

        Returns:
            Row_index_vec: index of rows (axis 0)
            Col_index_vec: index of cols (axis 1)
        """
        return self.Row_index_vec, self.Col_index_vec

    def get_vec_data(self):
        """
            returns 1d array data (nan free) [R_idx_vdc, A_idx_vec, R_off_vec, A_off_vec, Ccp_off_vec, Ccs_off_vec, Lon_off_vec, Lat_off_vec, Nan_mask_vec]
            if present will also include X_off_vec, Y_off_vec, and Phase_vec

            Note; please be aware of the order of additional atrributes and which ones are present
        """
        data_to_return = [self.R_idx_vec,
                    self.A_idx_vec,
                    self.R_off_vec,
                    self.A_off_vec,
                    self.Ccp_off_vec,
                    self.Ccs_off_vec,
                    self.Lon_off_vec,
                    self.Lat_off_vec,
                    self.Nan_mask_vec,
                    self.Row_index_vec,
                    self.Col_index_vec,]
        
        attr_list = ['R_idx_vec','A_idx_vec','R_off_vec','A_off_vec',
                     'Ccp_off_vec','Ccs_off_vec','Lon_off_vec','Lat_off_vec',
                     'Nan_mask_vec','Row_index_vec','Col_index_vec']
        # add optional attributes
        if hasattr(self,'SNR_vec'):
            data_to_return.append(self.SNR_vec)
            attr_list.append('SNR_vec')

        if hasattr(self,'Mag_vec'):
            data_to_return.append(self.Mag_vec)
            attr_list.append('Mag_vec')
        
        if hasattr(self,'X_off_vec'):
            data_to_return.append(self.X_off_vec)
            data_to_return.append(self.Y_off_vec)
            attr_list.append('X_off_vec')
            attr_list.append('Y_off_vec')

        if hasattr(self,'Phase_vec'):
            data_to_return.append(self.Phase_vec)
            attr_list.append('Phase_vec')

        return data_to_return, attr_list

    def comp_ll_dist_matrix(self):
        """
            Computes distance matrix from lat lon data.
            it uses the haversine function to compute great circle distances accurately
            can be very slow...
        """
        ll = np.column_stack((self.Lat_off_vec,self.Lon_off_vec))
        self.Dist_mat = pairwise_distances(ll,ll,metric='haversine')
        return self.Dist_mat
    

        


    def prep_DBSCAN(self,mode,plot_hist,n_bins):
        """
            prepares data for DBSCAN (or HDBSCAN) 
            choose mode = 0 (default) to work with longitude, latitude, magnitude, sine, cosine  
            choose mode = 1 to work with  longitude, latitude, range offset, azimuth offset
            choose mode = 2 to work with longitude, latitude, magnitude, direction 
            choose plot_hist = 1 to plot histograms of normalised components
        """
        
        
        # calculate magnitude of displacement vector
        mag_vec = np.hypot(self.R_off_vec, self.A_off_vec)
        # calculate phase from north
        phase_vec = np.degrees(-np.arctan2(self.A_off_vec, self.R_off_vec)) + 90 + self.Heading
        phase_vec = np.where(phase_vec < 0, phase_vec + 360, phase_vec % 360)

        # calculate sin and cosine components for continuous signal (no disconitnuity from 359-> 0 degrees)
        cos_vec = np.cos(np.deg2rad(phase_vec))
        sin_vec = np.sin(np.deg2rad(phase_vec))
        # define component matrix
        if mode == 0:
            X_pre = np.column_stack((self.Lon_off_vec,
                                     self.Lat_off_vec,
                                     mag_vec,
                                     cos_vec,
                                     sin_vec))
        elif mode == 1:
            X_pre = np.column_stack((self.Lon_off_vec,
                                     self.Lat_off_vec,
                                     self.R_off_vec,
                                     self.A_off_vec))
            diff = -1
        elif mode == 2:
            X_pre = np.column_stack((self.Lon_off_vec,
                                     self.Lat_off_vec,
                                     mag_vec,
                                     phase_vec))
            diff = -1
        else:
            print('ERROR: mode must be either 0 (default), 1, or 2')

        X = pre.StandardScaler().fit_transform(X_pre)
        if plot_hist == 1:
            fig3, ax = plt.subplots(1, 5, figsize=(8, 8))
            ax[0].hist(X[:, 0], n_bins)
            ax[1].hist(X[:, 1], n_bins)
            ax[2].hist(X[:, 2], n_bins)
            ax[3].hist(X[:, 3], n_bins)
            if mode == 0:
                ax[4].hist(X[:, 4], n_bins)
        
        self.X = X
        self.X_pre = X_pre
        return self.X_pre, self.X, np.sum(diff)
    
    def run_PCA(self,n_comp):
        """
        performs principle component analysis prior to outlier detection with (H)DBSCAN.
        works on the self.X data. 

        Args:
            n_comp (int): number of components to calculate and return

        Returns:
            X_pca (np.ndarray): principle components of the input data
        """
        PCA_obj = PCA(n_components=n_comp)
        self.X_pca = PCA_obj.fit_transform(self.X)
        return self.X_pca
    
    def run_DBSCAN(self,eps, min_samples,leaf_size=30,algorithm='auto',pca_flag=1):
        """
        method to perfrom DBSCAN.
        Note, works on the self.X_pca data unless pca_flag == 0
        DBSCAN is very slow for large datasets, consider using HDBSCAN

        Args:
            eps (float): maximum distance between points in cluster
            min_samples (int): minimum number of points in a cluster
            leaf_size (int): distance tree leaf size for neighborhood search
            algorithm (categorical): distance matrix algorithm (auto (default),KD-tree,ball-tree)
            pca_flag (bool): if 1 (default) run on pca data, if 0, run on normalised input without pca
        """
        clf_db = DBSCAN(eps=eps, min_samples=min_samples,leaf_size=leaf_size,algorithm = algorithm)
        db = clf_db.fit(self.X)
        self.DBSCAN_labels = db.labels_

    def rem_outliers_DBSCAN(self):
        """
            removes outliers found using DBSCAN
        """
        arr_shape = np.shape(self.R_off)
        nan_mask = self.DBSCAN_labels==-1 # outliers are class -1
        self.A_off = np.reshape(np.where(nan_mask,np.nan,self.A_off),arr_shape)
        self.R_off = np.reshape(np.where(nan_mask,np.nan,self.R_off),arr_shape)
        self.Ccp_off = np.reshape(np.where(nan_mask,np.nan,self.Ccp_off),arr_shape)
        self.Ccs_off = np.reshape(np.where(nan_mask,np.nan,self.Ccs_off),arr_shape)
        self.Lat_off = np.reshape(np.where(nan_mask,np.nan,self.Lat_off),arr_shape)
        self.Lon_off = np.reshape(np.where(nan_mask,np.nan,self.Lon_off),arr_shape)
        # compute for optional attributes
        if hasattr(self,'SNR'):
            self.SNR = np.reshape(np.where(nan_mask,np.nan,self.SNR),arr_shape)
        if hasattr(self,'X_off'): 
            self.X_off = np.reshape(np.where(nan_mask,np.nan,self.X_off),arr_shape)
            self.Y_off = np.reshape(np.where(nan_mask,np.nan,self.Y_off),arr_shape)
        if hasattr(self,'Phase'):
            self.Phase = np.reshape(np.where(nan_mask,np.nan,self.Phase),arr_shape)
        self.Nan_mask2 = np.reshape(nan_mask,arr_shape)

    def run_HDBSCAN(self,min_cluster_size,min_samples,single_cluster,cluster_selection_epsilon):
        """
            function to perform HDBSCAN
        """
        clf_hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples = min_samples, allow_single_cluster=single_cluster, cluster_selection_epsilon=cluster_selection_epsilon)
        hdb = clf_hdb.fit(self.X)
        self.HDBSCAN_labels = hdb.labels_
        self.HDBSCAN_outlier_scores = hdb.outlier_scores_

    def rem_outliers_HDBSCAN(self):
        """
            removes outliers found using HDBSCAN
        """
        arr_shape = np.shape(self.R_off)
        nan_mask = self.HDBSCAN_labels==-1 # outliers are class -1
        self.A_off = np.reshape(np.where(nan_mask,np.nan,self.A_off),arr_shape)
        self.R_off = np.reshape(np.where(nan_mask,np.nan,self.R_off),arr_shape)
        self.Ccp_off = np.reshape(np.where(nan_mask,np.nan,self.Ccp_off),arr_shape)
        self.Ccs_off = np.reshape(np.where(nan_mask,np.nan,self.Ccs_off),arr_shape)
        self.Lat_off = np.reshape(np.where(nan_mask,np.nan,self.Lat_off),arr_shape)
        self.Lon_off = np.reshape(np.where(nan_mask,np.nan,self.Lon_off),arr_shape)
        # compute for optional attributes
        if hasattr(self,'SNR'):
            self.SNR = np.reshape(np.where(nan_mask,np.nan,self.SNR),arr_shape)
        if hasattr(self,'X_off'): 
            self.X_off = np.reshape(np.where(nan_mask,np.nan,self.X_off),arr_shape)
            self.Y_off = np.reshape(np.where(nan_mask,np.nan,self.Y_off),arr_shape)
        if hasattr(self,'Phase'):
            self.Phase = np.reshape(np.where(nan_mask,np.nan,self.Phase),arr_shape)
        self.Nan_mask2 = np.reshape(nan_mask,arr_shape)


        def calc_local_L2(self):
            """ calculates local outlier disimilarity score

            Returns:
                _type_: _description_
            """

            from sklearn.metrics.pairwise import haversine_distances

            power = 2

            # get vector info
            self.wL2 = np.full(np.shape(self.X_off),np.nan)
            for idx in range(len(self.X_off_vec)):
                if np.mod(idx,1000)==0:
                    print(idx)
                    
                q_vec = (self.X_off_vec[idx], self.Y_off_vec[idx])
                q_pos = (self.Lon_off_vec[idx], self.Lat_off_vec[idx])
                q_r_idx = int(self.R_idx_vec[idx])
                q_a_idx = int(self.A_idx_vec[idx])


                # how much to overlap?
                # window has some overlap if n*step_size<window_size
                region_filter = (np.where((np.abs(self.R_idx_vec-q_r_idx)<self.R_win) &
                                          (np.abs(self.A_idx_vec-q_a_idx)<self.A_win) & 
                                          (self.R_idx_vec != q_r_idx) & 
                                          (self.A_idx_vec != q_a_idx)))
                
                if np.sum(region_filter)==0:
                    continue
                Q_region_r_idx = self.R_idx_vec[region_filter]
                Q_region_a_idx = self.A_idx_vec[region_filter]

                # get distances
                lons_Q_region = self.Lon_off_vec[region_filter]
                lats_Q_region = self.Lat_off_vec[region_filter]
                Dx = self.X_off_vec[region_filter]-q_vec[0]
                Dy = self.Y_off_vec[region_filter]-q_vec[1]

                Q_lonlat = np.column_stack((lons_Q_region,lats_Q_region))
                dists = haversine_distances(Q_lonlat, np.reshape(q_pos,(1,-1)))
                weights = 1/(dists**power)
                weights = weights/np.sum(weights)
                self.wL2[self.Row_index_vec[idx],self.Col_index_vec[idx]] = np.sum(np.hypot(Dx,Dy)*weights)/np.size(dists)
            return self.wL2

