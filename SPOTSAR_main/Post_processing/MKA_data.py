class MKA_data:
    """
    convinient class-object for data gathering. 
    Attr:
    MKA_R_off_vec (1D np.array):   Range offset results from Multi-kernel averaging as 1D array (no NaNs)
    MKA_A_off_vec (1D np.array):   Azimuth offset results from Multi-kernel averaging as 1D array (no NaNs)
    Lon_off_MKA_vec (1D np.array):   Longitude as 1D array (no NaNs)
    Lat_off_MKA_vec (1D np.array):   Latitude as 1D array (no NaNs)

    MKA_R_off (2D np.array):   Range offset results from Multi-kernel averaging
    MKA_A_off (2D np.array):   Azimuth offset results from Multi-kernel averaging
    Lon_off_MKA (2D np.array):   Longitude
    Lat_off_MKA (2D np.array):   Latitude
    """

    def __init__(self,mka_R_off_vec, mka_A_off_vec, lon_off_MKA_vec, lat_off_MKA_vec, mka_R_off, mka_A_off, lon_off_MKA, lat_off_MKA):
        self.MKA_R_off_vec = mka_R_off_vec
        self.MKA_A_off_vec = mka_A_off_vec
        self.Lon_off_MKA_vec = lon_off_MKA_vec
        self.Lat_off_MKA_vec = lat_off_MKA_vec
        self.MKA_R_off = mka_R_off
        self.MKA_A_off = mka_A_off
        self.Lon_off_MKA = lon_off_MKA
        self.Lat_off_MKA = lat_off_MKA
