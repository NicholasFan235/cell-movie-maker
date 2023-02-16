import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

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

class TimepointPlotter:
    def __init__(self, **plot_kwargs):
        self.plot_kwargs = plot_kwargs
        self.cmap = False
    
    def plot_stroma(self, ax, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        ax.scatter(
            data.x, data.y,
            color='lightblue', alpha=0.5,
            **self.plot_kwargs)

    def plot_tumour(self, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        if self.cmap:
            ax.scatter(
                data.x, data.y, cmap=truncate_colormap('Purples', 0.2, 0.8),
                c=1-data.damage, vmin=0.1, vmax=0.9, **self.plot_kwargs)
        else:
            ax.scatter(data.x, data.y, c='purple', **self.plot_kwargs)

    def plot_cytotoxic(self, ax, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data
        if self.cmap:
            ax.scatter(data.x, data.y, cmap=truncate_colormap('YlGn', 0, 0.6),
                c=data.potency, vmin=0.1, vmax=0.9, **self.plot_kwargs)
        else:
            ax.scatter(data.x, data.y, c='darkorange', **self.plot_kwargs)
        
    def plot_macrophages(self, ax, simulation_timepoint):
        data = simulation_timepoint.macrophages_data
        ax.scatter(
            data.x, data.y,
            color='lightgreen', alpha=0.5,
            **self.plot_kwargs)

    def plot(self, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        self.plot_stroma(ax, simulation_timepoint)
        self.plot_tumour(ax, simulation_timepoint)
        self.plot_cytotoxic(ax, simulation_timepoint)
        self.plot_macrophages(ax, simulation_timepoint)


class HistogramPlotter:
    def __init__(self, **plot_kwargs):
        self.plot_kwargs = plot_kwargs
    
    def cytotoxic_histogram(self, ax, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data.potency.to_numpy()
        data[data < 0] = 0
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('CD8+ Potency')
    
    def tumour_histogram(self, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data.damage.to_numpy()
        data[data > 1] = 1
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('Tumour Accumulated Damage')
    