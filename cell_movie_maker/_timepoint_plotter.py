import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import dataclasses

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
    @dataclasses.dataclass
    class Config:
        plot_kwargs = {}
        cmap = False
    
    def plot_stroma(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        data = simulation_timepoint.stroma_data
        ax.scatter(
            data.x, data.y,
            color='lightblue', alpha=0.5,
            **config.plot_kwargs)

    def plot_tumour(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        data = simulation_timepoint.tumour_data
        if config.cmap:
            ax.scatter(
                data.x, data.y, cmap=truncate_colormap('Purples_r', 0.2, 0.8),
                c=data.damage, vmin=0.1, vmax=0.9, **config.plot_kwargs)
        else:
            ax.scatter(data.x, data.y, c='purple', **config.plot_kwargs)

    def plot_cytotoxic(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        data = simulation_timepoint.cytotoxic_data
        if config.cmap:
            ax.scatter(data.x, data.y, cmap=truncate_colormap('YlGn', 0, 0.6),
                c=data.potency, vmin=0.1, vmax=0.9, **config.plot_kwargs)
        else:
            ax.scatter(data.x, data.y, c='darkorange', **config.plot_kwargs)
        
    def plot_macrophages(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        data = simulation_timepoint.macrophages_data
        ax.scatter(
            data.x, data.y,
            color='lightgreen', alpha=0.5,
            **config.plot_kwargs)
        
    def plot_blood_vessels(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        data = simulation_timepoint.blood_vessel_data
        ax.scatter(
            data.x, data.y,
            color='red', **config.plot_kwargs)

    def plot(fig, ax, simulation_timepoint, frame_num, timepoint, *, config=None):
        if config is None: config = TimepointPlotter.Config()

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        TimepointPlotter.plot_stroma(fig, ax, simulation_timepoint, config=config)
        TimepointPlotter.plot_tumour(fig, ax, simulation_timepoint, config=config)
        TimepointPlotter.plot_cytotoxic(fig, ax, simulation_timepoint, config=config)
        TimepointPlotter.plot_macrophages(fig, ax, simulation_timepoint, config=config)
        TimepointPlotter.plot_blood_vessels(fig, ax, simulation_timepoint, config=config)

class TumourTimepointPlotter:
    @dataclasses.dataclass
    class Config:
        plot_kwargs = {}
        cmap = False
    
    def plot_stroma(fig, ax, simulation_timepoint, *, config=None):
        data = simulation_timepoint.stroma_data
        ax.scatter(
            data.x, data.y,
            color='lightblue', alpha=0.5,
            **config.plot_kwargs)

    def plot_tumour(fig, ax, simulation_timepoint, *, config=None):
        data = simulation_timepoint.tumour_data
        necrotic = data[data.oxygen <= 0.01]
        hypoxic = data[(data.oxygen > 0.01) & (data.oxygen <= 0.01)]
        healthy = data[data.oxygen > 0.01]
        ax.scatter(necrotic.x, necrotic.y, c='white', **config.plot_kwargs)
        ax.scatter(hypoxic.x, hypoxic.y, c='yellow', **config.plot_kwargs)
        ax.scatter(healthy.x, healthy.y, c='purple', **config.plot_kwargs)

    def plot(fig, ax, simulation_timepoint, frame_num, timepoint, *, config=None):
        if config is None: config = TumourTimepointPlotter.Config()

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        TumourTimepointPlotter.plot_stroma(fig, ax, simulation_timepoint, config=config)
        TumourTimepointPlotter.plot_tumour(fig, ax, simulation_timepoint, config=config)

class HistogramPlotter:
    @dataclasses.dataclass
    class Config:
        plot_kwargs = {}
    
    def cytotoxic_histogram(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = HistogramPlotter.Config()
        data = simulation_timepoint.cytotoxic_data.potency.to_numpy()
        data[data < 0] = 0
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('CD8+ Potency')
    
    def tumour_histogram(fig, ax, simulation_timepoint, *, config=None):
        if config is None: config = HistogramPlotter.Config()
        data = simulation_timepoint.tumour_data.damage.to_numpy()
        data[data > 1] = 1
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('Tumour Accumulated Damage')
