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

class TimepointPlotterV2:
    def __init__(self):
        pass
    
    def plot_stroma(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='lightblue', alpha=0.5)
            ax.add_artist(artist)
        #ax.scatter(
        #    data.x, data.y,
        #    color='lightblue', alpha=0.5,
        #    **self.plot_kwargs)

    def plot_tumour(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        norm = mpl.colors.Normalize(vmin=0.1, vmax=0.9)
        cmap = truncate_colormap('Purples_r', 0.2, 0.9)
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='black', fc=cmap(norm(cell.damage)))
            ax.add_artist(artist)
        #if self.cmap:
        #    ax.scatter(
        #        data.x, data.y, cmap=truncate_colormap('Purples_r', 0.2, 0.8),
        #        c=data.damage, vmin=0.1, vmax=0.9, **self.plot_kwargs)
        #else:
        #    ax.scatter(data.x, data.y, c='purple', **self.plot_kwargs)

    def plot_cytotoxic(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='black', fc='darkorange',
                alpha=max(0.1, cell.potency))
            ax.add_artist(artist)
        #if self.cmap:
        #    ax.scatter(data.x, data.y, cmap=truncate_colormap('YlGn', 0, 0.6),
        #        c=data.potency, vmin=0.1, vmax=0.9, **self.plot_kwargs)
        #else:
        #    ax.scatter(data.x, data.y, c='darkorange', **self.plot_kwargs)
        
    def plot_macrophages(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.macrophages_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='lightgreen', alpha=0.5)
            ax.add_artist(artist)
        #ax.scatter(
        #    data.x, data.y,
        #    color='lightgreen', alpha=0.5,
        #    **self.plot_kwargs)
        
    def plot_blood_vessels(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.blood_vessel_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='red')
            ax.add_artist(artist)
        #ax.scatter(
        #    data.x, data.y,
        #    color='red', **self.plot_kwargs)

    def plot(self, fig, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        self.plot_stroma(fig, ax, simulation_timepoint)
        self.plot_macrophages(fig, ax, simulation_timepoint)
        self.plot_blood_vessels(fig, ax, simulation_timepoint)
        self.plot_tumour(fig, ax, simulation_timepoint)
        self.plot_cytotoxic(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_aspect(1.0, adjustable='box')


class TumourTimepointPlotterV2:
    def __init__(self, **plot_kwargs):
        self.plot_kwargs = plot_kwargs
        self.cmap = False
    
    def plot_stroma(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='lightblue', alpha=0.5)
            ax.add_artist(artist)

    def plot_tumour(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        for _, cell in data.iterrows():
            if cell.oxygen <= 0.01:
                # necrotic
                c = 'white'
            elif cell.oxygen <= 0.01:
                # hypoxic
                c = 'yellow'
            else:
                #healthy
                c = 'purple'
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='black', fc=c)
            ax.add_artist(artist)
    
    def plot_tumour(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        necrotic = data[data.oxygen <= 0.01]
        hypoxic = data[(data.oxygen > 0.01) & (data.oxygen <= 0.01)]
        healthy = data[data.oxygen > 0.01]
        ax.scatter(necrotic.x, necrotic.y, c='white', **self.plot_kwargs)
        ax.scatter(hypoxic.x, hypoxic.y, c='yellow', **self.plot_kwargs)
        ax.scatter(healthy.x, healthy.y, c='purple', **self.plot_kwargs)

    def plot_blood_vessels(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.blood_vessel_data
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='red')
            ax.add_artist(artist)

    def plot(self, fig, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        self.plot_stroma(fig, ax, simulation_timepoint)
        self.plot_blood_vessels(fig, ax, simulation_timepoint)
        self.plot_tumour(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_aspect(1.0, adjustable='box')

class PressureTimepointPlotterV2:
    def __init__(self):
        pass
        
    def plot_cells(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.data
        norm = mpl.colors.Normalize(vmin=0, vmax=data.pressure.max())
        cmap = mpl.colormaps['cividis']
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc=cmap(norm(cell.pressure)), alpha=0.8)
            ax.add_artist(artist)
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    def plot(self, fig, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} Pressure')
        
        self.plot_cells(fig, ax, simulation_timepoint)

        ax.relim()
        ax.set_aspect(1.0, adjustable='box')
    
class OxygenTimepointPlotterV2:
    def __init__(self):
        pass
        
    def plot_cells(self, fig, ax, simulation_timepoint):
        data = simulation_timepoint.data
        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap = mpl.colormaps['inferno']
        for _, cell in data.iterrows():
            artist = mpl.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc=cmap(norm(cell.oxygen)), alpha=0.8)
            ax.add_artist(artist)
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    def plot(self, fig, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} Oxygen')
        
        self.plot_cells(fig, ax, simulation_timepoint)

        ax.relim()
        ax.set_aspect(1.0, adjustable='box')