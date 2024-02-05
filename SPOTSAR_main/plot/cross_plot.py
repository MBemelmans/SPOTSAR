import matplotlib.pyplot as plt
from matplotlib import colors as mcolors 
import numpy as np

def cross_plot(obj,attr1,attr2,mode=0,bins=100,lognorm=0):
        """
            plots cross_plot as scatter (mode=0) or hist2d (mode=1)
            option to plot histogram colours on log scale
        """
        x_data = getattr(obj,attr1).ravel()
        y_data = getattr(obj,attr2).ravel()
        mask = [(~np.isnan(x_data)) & (~np.isnan(y_data))][0]

        x_data = x_data[mask]
        y_data = y_data[mask]
        if mode == 0:
            fig1, ax0 = plt.subplots(figsize=(12,12))
            ax0.scatter(x_data,y_data,5)
        else:
            fig1, ax0 = plt.subplots(figsize=(12,12))
            if lognorm==0:
                ax0.hist2d(x_data,y_data,bins)
            
            if lognorm==1:
                ax0.hist2d(x_data,y_data,bins,norm=mcolors.LogNorm())