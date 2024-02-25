import numpy as np

def angle_between(v1, v2):
    """ Calculates the angle in radians between vectors 'v1' and 'v2':
        v1, v2 : 1-D numpy arrays
        Returns:
        Angle (rad) between v1 qnd v2
    """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
