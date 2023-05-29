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
    import get_1deg_dist
    distance_meters = get_1deg_dist()

    # copy data to manipulate limits without messing with the original data
    attr_copy = copy.deepcopy(getattr(obj,attr))

    # change limits for nicer plotting
    attr_copy[attr_copy<attr_lims[0]] = attr_lims[0]
    attr_copy[attr_copy>attr_lims[1]] = attr_lims[1]

    # plotting
    fig1, axes = plt.subplots(1,1,figsize=(8,8))
    axes[0].imshow(shading,cmap=cm.grayC,alpha=0.5, extent=dem_extent)
    q = axes[0].quiver(obj.Lon_off[::step,::step],obj.Lat_off[::step,::step],
                    obj.X_off[::step,::step],obj.Y_off[::step,::step],
                    attr_copy[::step,::step],
                    scale=scale, 
                    width = 0.01, 
                    edgecolor='black',
                    linewidth=0.2)
    axes[0].set_ylim([np.min(obj.Lat_off_vec),np.max(obj.Lat_off_vec)])
    axes[0].set_xlim([np.min(obj.Lon_off_vec),np.max(obj.Lon_off_vec)])
    axes[0].add_artist(ScaleBar(distance_meters,location='lower right'))
    fig1.colorbar(q,ax=axes[0],extend='both')
    qk = axes[0].quiverkey(q,
                             0.5,
                             0.9,
                             qk_length,
                             str(qk_length) +' m displacement in slant range–azimuth plane',
                             labelpos = 'E',
                             coordinates='figure')
    axes[0].set_title(f'{attr}: min = {np.max([np.min(attr_copy),attr_lims[0]])} max = {np.min([np.max(attr_copy),attr_lims[1]])}')
