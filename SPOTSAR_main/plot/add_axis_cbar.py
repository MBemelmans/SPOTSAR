import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms


def add_bottom_cax(ax, pad, height):
    """ Adds axis under selected axis to be used for a colourbar
    """
    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(
        axpos.x0,
        axpos.y0 - pad - height,
        axpos.x1,
        axpos.y0 - pad
    )
    cax = ax.figure.add_axes(caxpos)

    return cax

def add_right_cax(ax, pad, width):
    """ Adds axis right of selected axis to be used for a colourbar
    """
    axpos = ax.get_position()
    caxpos = mtransforms.Bbox.from_extents(
        axpos.x1 + pad,
        axpos.y0,
        axpos.x1 + pad + width,
        axpos.y1
    )
    cax = ax.figure.add_axes(caxpos)

    return cax