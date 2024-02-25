import numpy as np

def Run_MKA(q_obj,indeces=[],window_size=1,comp_lim=0.5,CI_lim=5):
        """
        Run Multi-kernel averaging where user can define seleced indices from the stack, 
        desired window size, and a completion factor as a high pass filter

        Input:
            q_obj (multi_kernel class objects): multi-kernel (multi-window) data object for the image pair in question.

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
        # get stack data
        if indeces==[]:
            stack_R = [obj.R_off for obj in q_obj.Stack]
            stack_A = [obj.A_off for obj in q_obj.Stack]
            stack_ccp = [obj.Ccp_off for obj in q_obj.Stack]
            stack_ccs = [obj.Ccs_off for obj in q_obj.Stack]
        else:
            substack = [q_obj.Stack[i] for i in indeces]
            stack_R = np.stack([obj.R_off for obj in substack],axis=0)
            stack_A = np.stack([obj.A_off for obj in substack],axis=0)
            stack_ccp = np.stack([obj.Ccp_off for obj in substack],axis=0)
            stack_ccs = np.stack([obj.Ccs_off for obj in substack],axis=0)

        # create list of maps to make 
        avg_maps = []
        offset = window_size // 2

        for stack in [stack_R,stack_A]:
            # set window size according to stack dimensions
            window_shape = (stack.shape[0], window_size, window_size)
            print(np.shape(window_shape))
            # define shape of multi-kernel averaged map (same as input data), filled with nan
            Avg_map = np.full(stack.shape[1:], np.nan)
            
            # use np.lib.stride_tricks.sliding_window_view to devided data into windows
            # 1.2xfaster than sklearn view_as_windows
            win_data = np.lib.stride_tricks.sliding_window_view(stack, window_shape)[0]



            # remove data that is nan for too many different window sizes
            nan_frac = np.sum(np.isnan(win_data), axis=2) / (window_size ** 2)
            nan_frac = nan_frac/np.shape(win_data)[2]
            nan_frac[nan_frac > comp_lim] = np.nan
            nan_frac[nan_frac <= comp_lim] = 1
            win_data = np.multiply(win_data, nan_frac[..., np.newaxis])

            # # define shape of multi-kernel averaged map (same as input data), filled with nan
            Avg_map = np.full(stack.shape[1:], np.nan)

            # per window, go take 95% confidence interval data and take average (mean)
            for win_i in range(win_data.shape[0]):
                if win_i % 50 == 2:
                    print('win_i', win_i)
                    print('win',win.flatten(),'mean',np.nanmean(win), 'z_score',z_score.flatten())
                for win_j in range(win_data.shape[1]):
                    offset = window_size // 2
                    # extract relevant window
                    win = win_data[win_i, win_j]
                    # calculate 95 % confidence interval
                    if np.sum(~np.isnan(win))==1:
                         Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)
                    elif CI_lim == 0:
                         Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)
                    else:
                        data_std = np.nanstd(win)
                        data_mean = np.nanmean(win)
                        z_score = (win-data_mean)/data_std
                        mask = np.abs(z_score) > 1 # 95 conf interval
                        win[mask] = np.nan
                        Avg_map[win_i + offset, win_j + offset] = np.nanmean(win)


            avg_maps.append(Avg_map)
        q_obj.MKA_R_off = avg_maps[0]
        q_obj.MKA_A_off = avg_maps[1]

        return q_obj.MKA_R_off, q_obj.MKA_A_off
