def plot_rand_vec(obj,idx,step,border=0.05,alpha=0.3,power=2):
        """
        Highlights a random vector in the offset map to assess if the vector is a outlier.
        Also calculates local weighted L2 based on overlapping region (windowsize-stepsize dependent)

        Args:
            obj: single kernel object
            idx (int): index of random vector
            border (float, optional): Local region to plot vector_coords +/- border. 
                                      Defaults to 0.05.
            alpha (float, optional): opacity of not selected pixels. Defaults to 0.3.
            power (float, optional): inverse distance weighting exponent. Defaults to 2. 

        Returns:
            _type_: _description_
        """

        # get vector info
        q_vec = (obj.X_off_vec[idx], obj.Y_off_vec[idx])
        q_pos = (obj.Lon_off_vec[idx], obj.Lat_off_vec[idx])
        q_r_idx = obj.R_idx_vec[idx]
        q_a_idx = obj.A_idx_vec[idx]

        # how much to overlap?
        # window has some overlap if n*step_size<window_size
        region_filter = (np.where(np.abs(obj.R_idx_vec-q_r_idx)<obj.R_win) & np.where(np.abs(obj.A_idx_vec-q_a_idx)<obj.A_win))

        # get larger filter for plotting neighborhood
        region_filter2 = (np.where((np.abs(obj.R_idx_vec-q_r_idx)<3*obj.R_win) & (np.abs(obj.A_idx_vec-q_a_idx)<3*obj.A_win)))


        Q_region_r_idx = obj.R_idx_vec[region_filter]
        Q_region_a_idx = obj.A_idx_vec[region_filter]

        # get distances
        lons_Q_region = obj.Lon_off[region_filter]
        lats_Q_region = obj.Lat_off[region_filter]
        Q_lonlat = np.column_stack(lons_Q_region,lats_Q_region)
        dists = haversine_distances(Q_lonlat, q_pos)
        weights = 1/(dists**power)
        weights = weights/np.sum(weights)

        Dx = obj.X_off_vec[region_filter]-q_vec[0]
        Dy = obj.Y_off_vec[region_filter]-q_vec[1]
        
        wL2 = np.sum(np.hypot(Dx,Dy)*weights)

        fig=plt.figure(figsize=(10,10))
        gs=GridSpec(1,1) # 2 rows, 2 columns
        ax1=fig.add_subplot(gs[0,0]) # First row, first column

        ax1.quiver(
                obj.Lon_off_vec[::step],
                obj.Lat_off_vec[region_filter2],
                obj.X_off_vec[region_filter2],
                obj.Y_off_vec[region_filter2],
                facecolor = 'black',
                scale=50, width = 0.005,
                edgecolor="k", alpha = 0.3
            )

        qv = ax1.quiver(
                0,
                0,
                1,
                0,
                facecolor = 'black',
                scale=50, width = 0.005,
                edgecolor="k", alpha = 1
            )
        ax1.quiverkey(qv,0.5,0.95,3,'Displacement (3m)', labelpos = 'E',coordinates='figure')
        ax1.set_xlim([q_pos[0]-border, q_pos[0]+border])
        ax1.set_ylim([q_pos[1]-border, q_pos[1]+border])
        ax1.set_title(f'{q_r_idx},{q_a_idx},{wL2}')