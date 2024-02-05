def pair_plot(obj,mode):
        """
            plots joint pdf for all combinations of attributed used in DBSCAN or HDBSCAN
        """
        if mode == 0:
            X_pre_df = pd.DataFrame(obj.X_pre,columns=('Lon','Lat','Mag','Dir_x','Dir_y'))
        if mode == 1:
            X_pre_df = pd.DataFrame(obj.X_pre,columns=('Lon','Lat','R_off','A_off'))
        sns.pairplot(X_pre_df, diag_kind='kde',kind='hist')