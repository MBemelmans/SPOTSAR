import numpy as np

def get_sar_vector(heading, inc):
    # we assume right looking
    flight_dir = -heading
    P_los= [np.sin(np.deg2rad(inc))*np.cos(np.deg2rad(flight_dir)),
            np.sin(np.deg2rad(inc))*np.sin(np.deg2rad(flight_dir)),
            -np.cos(np.deg2rad(inc))]
    
    P_azi = [np.cos(np.deg2rad(flight_dir+90)),
             np.sin(np.deg2rad(flight_dir+90)),
             0]
    return P_los, P_azi