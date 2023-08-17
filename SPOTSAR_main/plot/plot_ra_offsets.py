import copy
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.gridspec import GridSpec

from cmcrameri import cm
from .get_1deg_dist import get_1deg_dist

import pyproj
from pyproj import CRS
def plot_ra_offsets(obj,shading,dem_extent,clims,grid_size=1000,lat_lims=[],lon_lims=[],cmap=cm.vik):
    # get length of 1 deg. for scalebar
    distance_meters = get_1deg_dist()
        # change limits for nicer plotting
    R_off = getattr(obj,'R_off')
    A_off = getattr(obj,'A_off')
    Lon_off = getattr(obj,'Lon_off')
    Lat_off = getattr(obj,'Lat_off')
    

    if lat_lims == []:
        lat_lims = [np.min(Lat_off),np.max(Lat_off)]
    
    if lon_lims == []:
        lon_lims = [np.min(Lon_off),np.max(Lon_off)]

    # plotting
    fig1, axes = plt.subplots(2,1,figsize=(8,8))
    axes[0].imshow(shading,cmap=cm.grayC,alpha=0.5, extent=dem_extent)
    axes[1].imshow(shading,cmap=cm.grayC,alpha=0.5, extent=dem_extent)

    plot_data = axes[0].hexbin(Lon_off.flatten(),Lat_off.flatten(),C=R_off.flatten(),gridsize=grid_size,cmap=cmap,vmin=clims[0],vmax=clims[1])
    axes[0].set_xlim(lon_lims)
    axes[0].set_ylim(lat_lims)
    axes[0].set_aspect('equal', 'box')
    axes[0].add_artist(ScaleBar(distance_meters,location='lower left'))
    # axes[0].set_axis_off()
    cbar = plt.colorbar(plot_data,ax=axes[0])
    cbar.set_label('Slant range offset [m]')

    plot_data = axes[1].hexbin(Lon_off.flatten(),Lat_off.flatten(),C=A_off.flatten(),gridsize=grid_size,cmap=cmap,vmin=clims[0],vmax=clims[1])
    axes[1].set_xlim(lon_lims)
    axes[1].set_ylim(lat_lims)
    axes[1].set_aspect('equal', 'box')
    axes[1].add_artist(ScaleBar(distance_meters,location='lower left'))
    # axes[0].set_axis_off()
    cbar = plt.colorbar(plot_data,ax=axes[1])
    cbar.set_label('Azimuth offset [m]')
    