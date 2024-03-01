import copy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.gridspec import GridSpec

from cmcrameri import cm

import pyproj
from pyproj import CRS


from .add_axis_cbar import add_right_cax

def plot_vec_attr_arrays(Lons,Lats,R_off,A_off,attr,step,scale,width =0.005 ,attr_lims=[0,1],qk_length=1,shading = [], dem_extent = [], lat_lims = [], lon_lims = [],qk_pos = [0.05,0.05]):
    """
    Plots displacement as vectors in slantrange - azimuth plane and 
    assigns colour based on attribute value and limits

    Args:
        Lons (np.array): longitude 
        Lats (np.array): latitude 
        X_off (np.array): X projected offset 
        Y_off (np.array): Y_projected offset 
        attr (np.array): attribute used fo colourscale
        step (int): descimation factor of data to plot
        scale (int): scale of the arrows
        attr_lims (list of floats, optional): attribute limits. Defaults to [0,1]
        qk_length (float, optional): length of arrow in arrow legend. Defaults to 1
        shading (np.array, optional): background shading (hillshade) data. Defaults to [] -> do not use.
        dem_extent (list, optional): extent of shading data. Defaults to [] -> do not use.
        lat_lims (list, optional): latitude limits of area to plot. Defaults to [] -> do not use.
        lon_lims (list, optional): longitude limits of area to plot. Defaults to [] -> do not use.
    """
    # # get length of 1 deg. for scalebar
    # from sm.plot import get_1deg_dist
    # distance_meters = get_1deg_dist()

    # copy data to manipulate limits without messing with the original data
    if attr != []:
        # change limits for nicer plotting
        attr[attr<attr_lims[0]] = attr_lims[0]
        attr[attr>attr_lims[1]] = attr_lims[1]

    if lat_lims == []:
        lat_lims = [np.min(Lats),np.max(Lats)]
    
    if lon_lims == []:
        lon_lims = [np.min(Lons),np.max(Lons)]

    # decimation factor
    all_idx = [i for i in range(len(R_off))]
    n_points = np.ceil(len(R_off)/step)
    # select points at random
    sel_idx = np.random.choice(all_idx,int(n_points),replace=False)

    # plotting
    fig1, axes = plt.subplots(1,1,figsize=(8,8))
    if (dem_extent != []):
        axes.imshow(shading,cmap=cm.grayC,alpha=0.5, extent=dem_extent)
    
    if attr == []:
        q = axes.quiver(Lons[sel_idx],Lats[sel_idx],
                        R_off[sel_idx],A_off[sel_idx],
                        color='black',
                        scale=scale, 
                        width = width, 
                        edgecolor='black',
                        linewidth=0.2)
    else:
        q = axes.quiver(Lons[sel_idx],Lats[sel_idx],
                        R_off[sel_idx],A_off[sel_idx],
                        attr[sel_idx],
                        scale=scale, 
                        width = width, 
                        edgecolor='black',
                        linewidth=0.2)
    axes.set_ylim(lat_lims)
    axes.set_xlim(lon_lims)
    axes.add_artist(ScaleBar(110123.8,location='lower right',font_properties={'size': 40}))
    cax = add_right_cax(axes,0.02,0.03)
    fig1.colorbar(q,cax=cax,label='2D displacement magnitude [m]')
    qk = axes.quiverkey(q,
                             qk_pos[0],
                             qk_pos[1],
                             qk_length,
                             str(qk_length) +' m displacement in\nslant range–azimuth plane',
                             labelpos = 'E',
                             coordinates='figure')
    # if attr != []:
        # axes.set_title(f'min = {np.nanmax([np.nanmin(attr),attr_lims[0]])} max = {np.nanmin([np.nanmax(attr),attr_lims[1]])}')
    return fig1, axes