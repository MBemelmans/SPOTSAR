import numpy as np
from numpy.linalg import lstsq


def remove_outliers(arr, confidence=95):
    print("removing outliers")
    lower_bound = (100 - confidence) / 2
    upper_bound = 100 - lower_bound

    lower_percentile = np.nanpercentile(arr, lower_bound, axis=(2, 3), keepdims=True)
    upper_percentile = np.nanpercentile(arr, upper_bound, axis=(2, 3), keepdims=True)
    arr_no_outliers = np.empty_like(arr)
    arr_no_outliers[arr < lower_percentile] = np.nan
    arr_no_outliers[arr > upper_percentile] = np.nan
    print("outliers removed")
    # arr_no_outliers = np.where(np.logical_and(arr >= lower_percentile, arr <= upper_percentile), arr, np.nan)
    return arr_no_outliers


def remove_plane(arr, x_coords, y_coords, deplane=False):
    print("remove plane")
    # reshape data so that they are Nxwin*win
    d_shape = np.shape(arr)
    x_flat = x_coords.reshape((d_shape[0] * d_shape[1], d_shape[2] * d_shape[3]))
    y_flat = y_coords.reshape((d_shape[0] * d_shape[1], d_shape[2] * d_shape[3]))
    arr_flat = arr.reshape((d_shape[0] * d_shape[1], d_shape[2] * d_shape[3]))
    # create ones array with same shape as data for lstsq plane fitting
    std_no_plane = np.full(np.shape(arr_flat)[0], np.nan)
    if deplane:
        for i in range(np.shape(arr_flat)[0]):
            if np.mod(i, 5000) == 0:
                print(i)
            win_x = x_flat[i]
            win_y = y_flat[i]
            win_d = arr_flat[i]

            # # Fit a plane using polyfit
            # coefficients = np.polyfit([win_x, win_y], win_d, deg=1)

            # # Extract the plane coefficients
            # a, b, c = coefficients

            # # Calculate the plane values at each coordinate
            # plane = a * X + b * Y + c

            # # Remove the plane from var_d
            # d_no_plane = win_d - plane
            # std_no_plane[i] = np.std(
            #     d_no_plane,
            # )

            ones = np.ones_like(win_d)

            # fit plane
            valid_indices_d = ~np.isnan(win_d)
            valid_indices_x = ~np.isnan(win_x)
            valid_indices_y = ~np.isnan(win_y)
            valid_indices = (valid_indices_d) & (valid_indices_x) & (valid_indices_y)
            if np.size(valid_indices) <= 4:
                std_no_plane[i] = np.nan
            else:
                A = np.column_stack(
                    (win_x[valid_indices], win_y[valid_indices], ones[valid_indices])
                )
                b = win_d[valid_indices]
                plane_coeffs, _, _, _ = lstsq(A, b)
                plane = np.dot(A, plane_coeffs)
                d_no_plane = b - plane
            arr_no_plane = np.reshape(d_no_plane, d_shape[0:2])
    print("Plane removed")
    return arr_no_plane


def sliding_window_std(data):
    arr = data[0]
    x_coords = data[1]
    y_coords = data[2]
    window_shape = (data[3], data[3])
    deplane = data[4]
    windows = np.lib.stride_tricks.sliding_window_view(arr, window_shape)
    x_windows = np.lib.stride_tricks.sliding_window_view(x_coords, window_shape)
    y_windows = np.lib.stride_tricks.sliding_window_view(y_coords, window_shape)

    windows_no_outliers = remove_outliers(windows)
    std_no_plane = np.empty_like(np.shape(windows)[0:2])
    if deplane:
        arr_no_plane = remove_plane(windows_no_outliers, x_windows, y_windows)
        print('calc std')
        std_no_plane = np.nanstd(arr_no_plane, axis=(2, 3))
        print('std calculated')
    else:
        print('calc std')
        for i in range(np.shape(windows)[0]):
            if np.mod(i,1000) == 0:
                print(i)
            for j in range(np.shape(windows)[1]):
                win = windows_no_outliers[i,j,:,:]
                std_no_plane[i,j] = np.nanstd(win)
        print('std calculated')

    return std_no_plane
