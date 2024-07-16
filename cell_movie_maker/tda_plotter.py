import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from scipy.spatial import Delaunay
from scipy.spatial.distance import cdist


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''
    https://stackoverflow.com/a/18926541
    '''
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def sub_cmap(cmap, vmin, vmax):
    return lambda v: cmap(vmin + (vmax - vmin) * v)

class RipsFiltrationPlotter:
    def plot_tumour_rips(fig, ax, tp):
        from ripser import Rips
        data = tp.tumour_data
        if len(data) > 0:
            rips = Rips(verbose=False)
            diagrams = rips.fit_transform(data[['x', 'y']])
            rips.plot(diagrams, ax=ax)
        ax.set_title('Rips Persistence Diagram for Tumour')
        ax.set_xlabel('Birth (Cell Diameters)')
        ax.set_ylabel('Death (Cell Diameters)')
    
    def plot_healthy_tumour_rips(fig, ax, tp):
        from ripser import Rips
        data = tp.tumour_data[tp.tumour_data.damage < 0.5]
        if len(data) > 0:
            rips = Rips(verbose=False)
            diagrams = rips.fit_transform(data[['x', 'y']])
            rips.plot(diagrams, ax=ax)
        ax.set_title('Rips Persistence Diagram for Healthy Tumour')
        ax.set_xlabel('Birth (Cell Diameters)')
        ax.set_ylabel('Death (Cell Diameters)')


    def plot_damaged_tumour_rips(fig, ax, tp):
        from ripser import Rips
        data = tp.tumour_data[tp.tumour_data.damage > 0.5]
        if len(data) > 0:
            rips = Rips(verbose=False)
            diagrams = rips.fit_transform(data[['x', 'y']])
            rips.plot(diagrams, ax=ax)
        ax.set_title('Rips Persistence Diagram for Damaged Tumour')
        ax.set_xlabel('Birth (Cell Diameters)')
        ax.set_ylabel('Death (Cell Diameters)')
