import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
from ..config import Config


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''
    https://stackoverflow.com/a/18926541
    '''
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def sub_cmap(cmap, vmin, vmax):
    return lambda v: cmap(vmin + (vmax - vmin) * v)

def load_info(sim, *, output_folder:pathlib.Path=None, cache:bool=True)->pd.DataFrame:
    if hasattr(sim, 'info'):
        info = sim.info
    else:
        info_file = output_folder if output_folder is not None else Config.output_folder
        info_file = info_file.joinpath(sim.name, 'info', f'{sim.id}.csv')
        info = pd.read_csv(info_file).set_index('timestep')
        if cache and sim is not None: sim.info = info
    return info