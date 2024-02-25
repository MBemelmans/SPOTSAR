import numpy as np

def get_MKA_vec(obj,R_STEP,A_STEP):
    """ retrieve MKA data for further (time series) processing

    Input: 
        obj (multi-kernel class object): data object containing MKA results
        R_STEP (int): step size in range direction in pixels
        A_STEP (int): step size in azimuth direction in pixels 
    """

    rng = np.linspace(obj.Limits[0],obj.Limits[1],int((obj.Limits[1]-obj.Limits[0])/R_STEP)+1)
    azi = np.linspace(obj.Limits[2],obj.Limits[3],int((obj.Limits[3]-obj.Limits[2])/A_STEP)+1)
    RNG, AZI = np.meshgrid(rng,azi)

    Lat_off = np.full(np.shape(RNG)[::-1], np.nan)
    Lon_off = np.full(np.shape(RNG)[::-1], np.nan)
    # find number of range estimates
    for d in obj.Mask_data:
        # fill arrays form indexes 
        Lat_off[d[11],d[12]] = d[9]
        Lon_off[d[11],d[12]] = d[10]
    setattr(obj,'Lon_off_MKA',Lon_off)
    setattr(obj,'Lat_off_MKA',Lat_off)
    
    nan_mask = np.isnan(obj.MKA_R_off)
    MKA_R_off_vec = obj.MKA_R_off[~nan_mask].ravel()
    MKA_A_off_vec = obj.MKA_A_off[~nan_mask].ravel()
    Lon_off_MKA_vec = obj.Lon_off_MKA[~nan_mask].ravel()
    Lat_off_MKA_vec = obj.Lat_off_MKA[~nan_mask].ravel()

    # set attributes
    setattr(obj,'MKA_R_off_vec', MKA_R_off_vec)
    setattr(obj,'MKA_A_off_vec', MKA_A_off_vec)
    setattr(obj,'Lon_off_MKA_vec', Lon_off_MKA_vec)
    setattr(obj,'Lat_off_MKA_vec', Lat_off_MKA_vec)

    # get map data
    MKA_R_off = obj.MKA_R_off
    MKA_A_off = obj.MKA_A_off
    Lon_off_MKA = obj.Lon_off_MKA
    Lat_off_MKA = obj.Lat_off_MKA

    return MKA_R_off_vec, MKA_A_off_vec, Lon_off_MKA_vec, Lat_off_MKA_vec, MKA_R_off, MKA_A_off, Lon_off_MKA, Lat_off_MKA
