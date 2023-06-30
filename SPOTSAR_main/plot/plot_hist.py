import matplotlib.pyplot as plt
import numpy as np


def plot_hist(obj, attr, n_bins, fig_ax=[], alpha=1, range=[], mask=[]):
    """
    plots histogram of attribute
    """
    if fig_ax == []:
        fig1, ax0 = plt.subplots(figsize=(12, 12))
    else:
        if len(fig_ax) == 1:
            ax0 = fig_ax
        elif len(fig_ax) == 2:
            fig1 = fig_ax[0]
            ax0 = fig_ax[1]
        else:
            print("axes not provided properly. for,mat should be (ax) or (fig,ax)")

    hist_data = getattr(obj, attr)
    if range == []:
        range = (np.nanmin(hist_data), np.nanmax(hist_data))
    if mask == []:
        ax0.hist(hist_data, n_bins, range, alpha=alpha)
    else:
        ax0.hist(hist_data[mask], n_bins, range, alpha=alpha)
