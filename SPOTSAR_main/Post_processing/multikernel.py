


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
            offset_data = dataset(file,[date_1,date_2],[r__win,a__win],self.Heading,[r_idx,a_idx,r_off,a_off,ccp_off,lat_off,lon_off,ccs_off])
            # do pre-stacking processing
            offset_data.calc_SNR()
            offset_data.calc_Mag()
            offset_data.calc_phase()
            offset_data.rotate_with_heading()
            offset_data.mask_nan_data()
            offset_data.rem_nans()
            
            self.Stack.append(offset_data)

        return self.Stack
    
    def Run_MKA(self,indices=[],window_size=1,comp_lim=0.5):
        """
        Run Multi-kernel averaging where user can define seleced indices from the stack, 
        desired window size, and a completion factor as a high pass filter

        Args:
            indices (list, optional): indices of slices from datastack used for MKA. Defaults to [], use all data.
            window_size (int, optional): window dimension for MKA, odd numbers 
                                         prefered because of pixel centering. 
                                         Defaults to 1.
            comp_lim (float, optional): completion limit between [0.0, 1.0]
                                        Only take data for MKA if more than 
                                        comp_lim of the stack is not nan. 
                                        Defaults to 0.5.

        Returns:
            avg_map: Multi-kernel Average map
        """

        if indeces==[]:
            stack = self.Stack
        else:
            stack = [self.Stack[i] for i in indices]

        window_shape = (stack.shape[0], window_size, window_size)
        # use view_as_windows to devided data into windows
        win_data = np.lib.stride_tricks.sliding_window_view(stack, window_shape)[0]
        # remove data that is nan for too many different window sizes
        nan_frac = np.sum(np.isnan(win_data), axis=2) / window_size ** 2
        nan_frac[nan_frac > comp_lim] = np.nan
        nan_frac[nan_frac <= comp_lim] = 1
        win_data = np.multiply(win_data, nan_frac[..., np.newaxis])
        # define shape of multi-kernel averaged map (same as input data), filled with nan
        self.Avg_map = np.full(stack.shape[1:], np.nan)
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
                self.Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)

        return self.Avg_map
    

