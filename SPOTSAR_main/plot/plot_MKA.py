from matplotlib.patches import Rectangle

idx_for_plot = [0,5,10,15]
zoom_extent = [140,240,310,390]

plot_data = [r_offset[idx] for idx in idx_for_plot]
plot_data.append(R_MKA)
plot_data = plot_data + [np.isnan(r_offset[idx]) for idx in idx_for_plot]
plot_data.append(np.isnan(R_MKA))
plot_data = plot_data + [r_offset[idx][zoom_extent[0]:zoom_extent[1],zoom_extent[2]:zoom_extent[3]] for idx in idx_for_plot]
plot_data.append(R_MKA[zoom_extent[0]:zoom_extent[1],zoom_extent[2]:zoom_extent[3]])

cmaps = [cm.vik,cm.vik,cm.vik,cm.vik,cm.vik,
         'Greys','Greys','Greys','Greys','Greys',
         cm.vik,cm.vik,cm.vik,cm.vik,cm.vik]
min_clim = [-vmax,-vmax,-vmax,-vmax,-vmax,
            0,0,0,0,0,
            -vmax,-vmax,-vmax,-vmax,-vmax]

max_clim = [vmax,vmax,vmax,vmax,vmax,
            1,1,1,1,1,
            vmax,vmax,vmax,vmax,vmax]
all_data_arrays2 = [all_data_arrays[idx] for idx in idx_for_plot]
win_sizes = ['window size (range, azimuth): ' + str(data.get_window_size()) for data in all_data_arrays2]
win_sizes = win_sizes + ['multi-kernel average']


# initiate figure
textsize = 15
plt.rc('font', size=textsize) 
fig=plt.figure(figsize=(20,12))
gs=GridSpec(3,5) # 3 rows, 5 columns
axes = [fig.add_subplot(gs[i,j]) for i in range(3) for j in range(5)]

for ax,p_data,cmap,clim_min,clim_max in zip(axes,plot_data,cmaps,min_clim,max_clim):
    ax.imshow(p_data,cmap=cmap,vmin=clim_min,vmax=clim_max, interpolation='Nearest')
    ax.set_axis_off()
    
for ax,win_size in zip(axes[0:5],win_sizes):
    ax.add_patch(plt.Rectangle((zoom_extent[2], zoom_extent[0]), zoom_extent[3]-zoom_extent[2], zoom_extent[1]-zoom_extent[0], ls="-", ec="k", fc="none",
                           ))
    ax.set_title(win_size)

fig.tight_layout()
cbar_pos = axes[0].get_position()
 
cax = plt.axes([cbar_pos.x0, cbar_pos.y0-0.04, cbar_pos.width, 0.02])      
mappable = plt.cm.ScalarMappable(cmap = cm.vik,
                                 norm = plt.Normalize(vmin = -vmax, vmax = vmax))
cbar = fig.colorbar(mappable, cax, orientation = 'horizontal')
cbar.set_label('Slant range offset', rotation=0, loc= 'center',labelpad=0)

for ax in axes[0:5]:
    ax.annotate('slant range',xy=(50,50),xytext=(0,-50),textcoords='offset pixels', xycoords='data',
                    arrowprops=dict(facecolor='black',arrowstyle='<-'),horizontalalignment='center',verticalalignment='top',rotation=90)
    ax.annotate('azimuth',xy=(50,50),xytext=(50,0),textcoords='offset pixels' ,xycoords='data',
                    arrowprops=dict(facecolor='black',arrowstyle='<-'),horizontalalignment='left',verticalalignment='center')

for ax in axes[-5:]:
    ax.annotate('slant range',xy=(5,5),xytext=(0,-50),textcoords='offset pixels', xycoords='data',
                    arrowprops=dict(facecolor='black',arrowstyle='<-'),horizontalalignment='center',verticalalignment='top',rotation=90)
    ax.annotate('azimuth',xy=(5,5),xytext=(50,0),textcoords='offset pixels' ,xycoords='data',
                    arrowprops=dict(facecolor='black',arrowstyle='<-'),horizontalalignment='left',verticalalignment='center')
