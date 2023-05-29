import matplotlib.pyplot as plt
import numpy as np

def plot_hist(obj,attr,n_bins,range=[],mask=[]):
        """
            plots histogram of attribute
        """
        hist_data = getattr(obj,attr)
        if range==[]:
            range = (np.nanmin(hist_data),np.nanmax(hist_data))
        if mask == []:
            fig1, ax0 = plt.subplots(figsize=(12,12))
            ax0.hist(hist_data,n_bins,range)
        else:
            fig1, ax0 = plt.subplots(figsize=(12,12))
            ax0.hist(hist_data[mask],n_bins,range)