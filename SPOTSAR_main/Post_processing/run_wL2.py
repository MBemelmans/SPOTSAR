# from sklearn import preprocessing as pre
# from sklearn.decomposition import PCA
# import numpy as np
# from numba import jit, njit, int32, float64
# from sklearn.metrics.pairwise import haversine_distances


# def run_wL2(X_off,X_off_vec,Y_off_vec,Lat_off_vec,Lon_off_vec,R_idx_vec,A_idx_vec,Row_index_vec,Col_index_vec,A_win,R_win):
#     power = 2
#     # get vector info
#     wL2 = np.full(np.shape(X_off),np.nan)   
#     for idx in range(np.shape(X_off_vec)[0]):
#         if np.mod(idx,1000)==0:
#             print(idx)
            
#         q_vec = (X_off_vec[idx], Y_off_vec[idx])
#         q_pos = (Lon_off_vec[idx], Lat_off_vec[idx])
#         q_r_idx = int(R_idx_vec[idx])
#         q_a_idx = int(A_idx_vec[idx])


#         # how much to overlap?
#         # window has some overlap if n*step_size<window_size
#         region_filter = (np.where((np.abs(R_idx_vec-q_r_idx)<R_win) &
#                                     (np.abs(A_idx_vec-q_a_idx)<A_win) & 
#                                     (R_idx_vec != q_r_idx) & 
#                                     (A_idx_vec != q_a_idx)))
        
#         if np.all(region_filter == 0):
#             continue
#         Q_region_r_idx = R_idx_vec[region_filter]
#         Q_region_a_idx = A_idx_vec[region_filter]

#         # get distances
#         lons_Q_region = Lon_off_vec[region_filter]
#         lats_Q_region = Lat_off_vec[region_filter]
#         Dx = X_off_vec[region_filter]-q_vec[0]
#         Dy = Y_off_vec[region_filter]-q_vec[1]

#         # Q_lonlat = np.column_stack((lons_Q_region,lats_Q_region))
#         # dists = haversine_distances(Q_lonlat, np.reshape(q_pos,(1,-1)))
#         # own haversine function (is not faster...)
#         dists = 2*np.arcsin(np.sqrt(np.sin((np.deg2rad(lats_Q_region)-np.deg2rad(q_pos[1]))/2)
#                                      + np.cos(np.deg2rad(lats_Q_region))*np.cos(np.deg2rad(q_pos[1]))
#                                      * np.sin((np.deg2rad(lons_Q_region)-np.deg2rad(q_pos[0]))/2)**2))

#         weights = 1/(dists**power)
#         weights = weights/weights.sum()
#         weighted_sum = weights*(np.sqrt(Dx**2 + Dy**2))
#         wL2[Row_index_vec[idx],Col_index_vec[idx]] = weighted_sum/np.shape(dists)[0]
#     return wL2

from sklearn import preprocessing as pre
from sklearn.decomposition import PCA
import numpy as np
from numba import jit, njit, int32, float64
from sklearn.metrics.pairwise import haversine_distances
from joblib import Parallel, delayed

def calculate_weighted_sum(idx, X_off_vec, Y_off_vec, Lat_off_vec, Lon_off_vec, R_idx_vec, A_idx_vec, Row_index_vec, Col_index_vec, A_win, R_win):
    power = 2
    q_vec = (X_off_vec[idx], Y_off_vec[idx])
    q_pos = (Lon_off_vec[idx], Lat_off_vec[idx])
    q_r_idx = int(R_idx_vec[idx])
    q_a_idx = int(A_idx_vec[idx])

    region_filter = (np.where((np.abs(R_idx_vec-q_r_idx)<R_win) &
                                (np.abs(A_idx_vec-q_a_idx)<A_win) & 
                                (R_idx_vec != q_r_idx) & 
                                (A_idx_vec != q_a_idx)))

    if np.sum(region_filter)==0:
        return np.nan

    Q_region_r_idx = R_idx_vec[region_filter]
    Q_region_a_idx = A_idx_vec[region_filter]
    lons_Q_region = Lon_off_vec[region_filter]
    lats_Q_region = Lat_off_vec[region_filter]
    Dx = X_off_vec[region_filter]-q_vec[0]
    Dy = Y_off_vec[region_filter]-q_vec[1]

    Q_lonlat = np.column_stack((lons_Q_region,lats_Q_region))
    dists = haversine_distances(Q_lonlat, np.reshape(q_pos,(1,-1)))
    # dists = 2*np.arcsin(np.sqrt(np.sin((np.deg2rad(lats_Q_region)-np.deg2rad(q_pos[1]))/2)
    #                              + np.cos(np.deg2rad(lats_Q_region))*np.cos(np.deg2rad(q_pos[1]))
    #                              * np.sin((np.deg2rad(lons_Q_region)-np.deg2rad(q_pos[0]))/2)**2))

    weights = 1/(dists**power)
    weights = weights/weights.sum()
    weighted_sum = weights*(np.sqrt(Dx**2 + Dy**2))
    return weighted_sum/np.shape(dists)[0]

def run_wL2(X_off,X_off_vec,Y_off_vec,Lat_off_vec,Lon_off_vec,R_idx_vec,A_idx_vec,Row_index_vec,Col_index_vec,A_win,R_win):
    wL2 = np.full(np.shape(X_off), np.nan)
    results = Parallel(n_jobs=-1)(delayed(calculate_weighted_sum)(idx, X_off_vec, Y_off_vec, Lat_off_vec, Lon_off_vec, R_idx_vec, A_idx_vec, Row_index_vec, Col_index_vec, A_win, R_win) for idx in range(np.shape(X_off_vec)[0]))
    for idx, result in enumerate(results):
        if np.mod(idx,1000) == 0:
            print(idx)
        wL2[Row_index_vec[idx], Col_index_vec[idx]] = result
    return wL2
