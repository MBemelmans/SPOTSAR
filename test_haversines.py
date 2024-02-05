import numpy as np
from sklearn.metrics.pairwise import haversine_distances
from math import radians, sin, cos, sqrt, atan2
import time

def optimized_haversine_distances(lonlat1, lonlat2):
    """
    Calculate the haversine distances between two sets of longitude-latitude coordinates.
    lonlat1: array-like, shape (n, 2)
        Array of longitude-latitude coordinates for the first set of points.
    lonlat2: array-like, shape (m, 2)
        Array of longitude-latitude coordinates for the second set of points.
    Returns:
    distances: ndarray, shape (n, m)
        Array of haversine distances between each pair of points.
    """
    lon1, lat1 = np.radians(lonlat1[:, 0]), np.radians(lonlat1[:, 1])
    lon2, lat2 = np.radians(lonlat2[:, 0]), np.radians(lonlat2[:, 1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distances = c * 6371.0  # Earth radius in kilometers

    return distances

# Generate random longitude-latitude coordinates
n = 1000
m = 1000
lonlat1 = np.random.uniform(low=-180, high=180, size=(n, 2))
lonlat2 = np.random.uniform(low=-180, high=180, size=(m, 2))

# Measure execution time for scikit-learn haversine_distances
start_time = time.time()
_ = haversine_distances(np.radians(lonlat1), np.radians(lonlat2))
sklearn_time = time.time() - start_time

# Measure execution time for optimized haversine_distances
start_time = time.time()
_ = optimized_haversine_distances(lonlat1, lonlat2)
optimized_time = time.time() - start_time

print(f"Execution time for scikit-learn haversine_distances: {sklearn_time:.6f} seconds")
print(f"Execution time for optimized haversine_distances: {optimized_time:.6f} seconds")
