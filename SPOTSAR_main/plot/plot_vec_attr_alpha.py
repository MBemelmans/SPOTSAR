import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm as mpl_cm
from matplotlib import colors as mcolors
from sklearn.metrics.pairwise import haversine_distances
from matplotlib.gridspec import GridSpec


import copy
from matplotlib_scalebar.scalebar import ScaleBar
from cmcrameri import cm
import pyproj
from pyproj import CRS


def plot_vec_attr_alpha(
    obj,
    attr,
    step,
    scale,
    width=0.005,
    attr_lims=[0, 1],
    qk_length=1,
    shading=[],
    dem_extent=[],
    lat_lims=[],
    lon_lims=[],
    alpha=0,
    fig_ax=[],
):
    """
    Plots displacement as vectors in slantrange - azimuth plane and
    assigns colour based on attribute value and limits

    Args:
        obj (class object): _description_
        attr (str): _description_
        step (int): _description_
        scale (int): _description_
        attr_lims (list of floats, optional): _description_. Defaults to [0,1]
        qk_length (float, optional): _description_. Defaults to 1
        shading (np.array, optional): _description_. Defaults to [] -> do not use.
        dem_extent (list, optional): _description_. Defaults to [] -> do not use.
        lat_lims (list, optional): _description_. Defaults to [] -> do not use.
        lon_lims (list, optional): _description_. Defaults to [] -> do not use.
    """
    # get length of 1 deg. for scalebar

    distance_meters = sm.plot.get_1deg_dist()

    # copy data to manipulate limits without messing with the original data
    if attr != []:
        attr_copy = copy.deepcopy(getattr(obj, attr))

        # change limits for nicer plotting
        alpha_map = np.ones_like(attr_copy)
        alpha_map[attr_copy < attr_lims[0]] = alpha
        attr_copy[attr_copy < attr_lims[0]] = attr_lims[0]
        attr_copy[attr_copy > attr_lims[1]] = attr_lims[1]

    if lat_lims == []:
        lat_lims = [np.min(obj.Lat_off_vec), np.max(obj.Lat_off_vec)]

    if lon_lims == []:
        lon_lims = [np.min(obj.Lon_off_vec), np.max(obj.Lon_off_vec)]

    # plotting
    if fig_ax == []:
        fig1, ax = plt.subplots(1, 1, figsize=(8, 8))
    else:
        fig1 = fig_ax[0]
        ax = fig_ax[1]

    if dem_extent != []:
        ax.imshow(shading, cmap=cm.grayC, alpha=0.5, extent=dem_extent)

    if attr == []:
        q = ax.quiver(
            obj.Lon_off[::step, ::step],
            obj.Lat_off[::step, ::step],
            obj.X_off[::step, ::step],
            obj.Y_off[::step, ::step],
            color="black",
            alpha=alpha_map[::step, ::step],
            scale=scale,
            width=width,
            edgecolor="black",
            linewidth=0.2,
        )
    else:
        q = ax.quiver(
            obj.Lon_off[::step, ::step],
            obj.Lat_off[::step, ::step],
            obj.X_off[::step, ::step],
            obj.Y_off[::step, ::step],
            attr_copy[::step, ::step],
            alpha=alpha_map[::step, ::step],
            scale=scale,
            width=width,
            edgecolor="black",
            linewidth=0.2,
            clim=attr_lims,
        )
    ax.set_ylim(lat_lims)
    ax.set_xlim(lon_lims)
    ax.add_artist(ScaleBar(distance_meters, location="lower right"))
    ax.set_axis_off()
    qk = ax.quiverkey(
        q,
        0.5,
        0.95,
        qk_length,
        str(qk_length) + " m displacement in slant range–azimuth plane",
        labelpos="E",
        coordinates="figure",
    )
    # if attr != []:
    #     ax.set_title(f'{attr}: min = {np.nanmax([np.nanmin(attr_copy),attr_lims[0]]):1.3f} max = {np.nanmin([np.nanmax(attr_copy),attr_lims[1]]):1.3f}')
    return q, fig, ax
