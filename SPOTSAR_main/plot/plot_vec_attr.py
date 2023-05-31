import copy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.gridspec import GridSpec

from cmcrameri import cm

import pyproj
from pyproj import CRS

def plot_vec_attr(obj,attr,step,scale,attr_lims,qk_length,shading = [],dem_extent = []):
    """
    Plots displacement as vectors in slantrange - azimuth plane and 
    assigns colour based on attribute value and limits

    Args:
        obj (class object): _description_
        attr (str): _description_
        step (int): _description_
        scale (int): _description_
        attr_lims (list, int): _description_
        qk_length (float): _description_
        shading (np.array, optional): _description_. Defaults to [] -> do not use.
        dem_extent (list, optional): _description_. Defaults to [] -> do not use.
    """
    # get length of 1 deg. for scalebar
    from .get_1deg_dist import get_1deg_dist
    distance_meters = get_1deg_dist()

    # copy data to manipulate limits without messing with the original data
    if attr != []:
        attr_copy = copy.deepcopy(getattr(obj,attr))

        # change limits for nicer plotting
        attr_copy[attr_copy<attr_lims[0]] = attr_lims[0]
        attr_copy[attr_copy>attr_lims[1]] = attr_lims[1]

    # plotting
    fig1, axes = plt.subplots(1,1,figsize=(8,8))
    if (dem_extent != []):
        axes.imshow(shading,cmap=cm.grayC,alpha=0.5, extent=dem_extent)
    
    if attr == []:
        q = axes.quiver(obj.Lon_off[::step,::step],obj.Lat_off[::step,::step],
                    obj.X_off[::step,::step],obj.Y_off[::step,::step],
                    color='black',
                    scale=scale, 
                    width = 0.01, 
                    edgecolor='black',
                    linewidth=0.2)
    else:
        q = axes.quiver(obj.Lon_off[::step,::step],obj.Lat_off[::step,::step],
                        obj.X_off[::step,::step],obj.Y_off[::step,::step],
                        attr_copy[::step,::step],
                        scale=scale, 
                        width = 0.01, 
                        edgecolor='black',
                        linewidth=0.2)
    axes.set_ylim([np.min(obj.Lat_off_vec),np.max(obj.Lat_off_vec)])
    axes.set_xlim([np.min(obj.Lon_off_vec),np.max(obj.Lon_off_vec)])
    axes.add_artist(ScaleBar(distance_meters,location='lower right'))
    fig1.colorbar(q,ax=axes,extend='both')
    qk = axes.quiverkey(q,
                             0.5,
                             0.95,
                             qk_length,
                             str(qk_length) +' m displacement in slant range–azimuth plane',
                             labelpos = 'E',
                             coordinates='figure')
    if attr != []:
        axes.set_title(f'{attr}: min = {np.nanmax([np.nanmin(attr_copy),attr_lims[0]])} max = {np.nanmin([np.nanmax(attr_copy),attr_lims[1]])}')
