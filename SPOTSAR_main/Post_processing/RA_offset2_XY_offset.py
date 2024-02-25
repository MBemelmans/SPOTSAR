import numpy as np

def RA_offset2_XY_offset(R_off,A_off,Heading):
    """
    calculates displacement in (quasi) E-W (x component) and (quasi) N-S (y component)
    """

    rot_mat = np.array(
        [
            [np.cos(np.deg2rad(Heading)), -np.sin(np.deg2rad(Heading))],
            [np.sin(np.deg2rad(Heading)),  np.cos(np.deg2rad(Heading))],
        ]
    )

    rot_vec = np.dot(np.column_stack((R_off, A_off)), rot_mat)

    X_off = rot_vec[:, 0]
    Y_off = rot_vec[:, 1]


    return X_off, Y_off