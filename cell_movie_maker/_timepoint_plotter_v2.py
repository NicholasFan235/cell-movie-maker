import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses


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

class TimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        p_max=None
        pressure_cmap='cividis'
        draw_colorbar=True
        ylim:tuple[int]=None
        xlim:tuple[int]=None

    def plot_stroma(fig, ax, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        for _, cell in data.iterrows():
            artist = matplotlib.patches.Circle((cell.x, cell.y), cell.radius,
                ec='none', fc='lightblue', alpha=0.5)
            ax.add_artist(artist)
        #ax.scatter(
        #    data.x, data.y,
        #    color='lightblue', alpha=0.5,
        #    **self.plot_kwargs)

    def plot_tumour(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        norm = matplotlib.colors.Normalize(vmin=0.1, vmax=0.9)
        cmap = truncate_colormap('Purples_r', 0.1, 0.75)
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='black', fc=cmap(norm(cell.damage))) for _, cell in data.iterrows()],
            edgecolors=None, facecolors = cmap(norm(data.damage.to_numpy())))
        ax.add_collection(collection)

    def plot_cytotoxic(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data
        if len(data) <= 0: return
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='darkorange', fc='darkorange', alpha=max(0.1, cell.potency)) for _, cell in data.iterrows()],
            edgecolors='darkorange', facecolors='darkorange')
        collection.set_alpha(np.maximum(0.1, data.potency.to_numpy()))
        ax.add_collection(collection)
        
    def plot_macrophages(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.macrophages_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='lightblue', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='lightblue')
        ax.add_collection(collection)
        
    def plot_blood_vessels(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.blood_vessel_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='red') for _, cell in data.iterrows()],
            edgecolors='none', facecolors='red')
        ax.add_collection(collection)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num:int, timepoint:int, *, sim=None, config:Config=None):
        if config is None: config = TimepointPlotterV2.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        TimepointPlotterV2.plot_stroma(fig, ax, simulation_timepoint)
        TimepointPlotterV2.plot_macrophages(fig, ax, simulation_timepoint)
        TimepointPlotterV2.plot_tumour(fig, ax, simulation_timepoint)
        TimepointPlotterV2.plot_blood_vessels(fig, ax, simulation_timepoint)
        TimepointPlotterV2.plot_cytotoxic(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')


class TumourTimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        ylim:tuple[int]=None
        xlim:tuple[int]=None

    def plot_stroma(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='lightblue', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='lightblue')
        ax.add_collection(collection)

    def plot_tumour(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, *, sim=None):
        data = simulation_timepoint.tumour_data
        patches = []
        colors = []
        for _, cell in data.iterrows():
            a = 0.01 if sim is None else sim.parameters['TumourNecroticConcentration']
            b = 0.01 if sim is None else sim.parameters['TumourHypoxicConcentration']
            if cell.oxygen <= a:
                # necrotic
                c = 'white'
            elif cell.oxygen <= b:
                # hypoxic
                c = 'darkorchid'
            else:
                #healthy
                c = 'purple'
            patches.append(matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='black', fc=c))
            colors.append(matplotlib.colors.to_rgba(c))
        collection = matplotlib.collections.PatchCollection(patches, edgecolors=np.array(colors), facecolors=np.array(colors))
        #collection.set_facecolors(np.array(colors))
        ax.add_collection(collection)

    def plot_blood_vessels(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.blood_vessel_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='red') for _, cell in data.iterrows()],
            edgecolors='none', facecolors='red')
        ax.add_collection(collection)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num:int, timepoint:int, *, sim=None, config=None):
        if config is None: config = TumourTimepointPlotterV2.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        TumourTimepointPlotterV2.plot_stroma(fig, ax, simulation_timepoint)
        TumourTimepointPlotterV2.plot_tumour(fig, ax, simulation_timepoint, sim=sim)
        TumourTimepointPlotterV2.plot_blood_vessels(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

class PressureTimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        p_max=None
        pressure_cmap='cividis'
        draw_colorbar=True
        ylim:tuple[int]=None
        xlim:tuple[int]=None

    def plot_cells(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, *, config:Config):
        data = simulation_timepoint.data
        norm = matplotlib.colors.Normalize(vmin=0, vmax=data.pressure.max() if config.p_max is None else config.p_max)
        cmap = matplotlib.colormaps[config.pressure_cmap]
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc=cmap(norm(cell.pressure)), alpha=0.8) for _, cell in data.iterrows()],
            edgecolors='none', facecolors=cmap(norm(data.pressure.to_numpy())))
        ax.add_collection(collection)
        if config.draw_colorbar: fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = PressureTimepointPlotterV2.Config()

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} Pressure')
        
        PressureTimepointPlotterV2.plot_cells(fig, ax, simulation_timepoint, config=config)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')
    
class OxygenTimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        ylim:tuple[int]=None
        xlim:tuple[int]=None

    def plot_cells(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.data
        norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
        cmap = matplotlib.colormaps['inferno']
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc=cmap(norm(cell.oxygen)), alpha=0.8) for _, cell in data.iterrows()],
            edgecolors='none', facecolors=cmap(norm(data.oxygen.to_numpy())))
        ax.add_collection(collection)
        fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = OxygenTimepointPlotterV2.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} Oxygen')
        
        OxygenTimepointPlotterV2.plot_cells(fig, ax, simulation_timepoint)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

class LiverMetTimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        ylim:tuple[int]=None
        xlim:tuple[int]=None

    def plot_background(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.background_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='lightblue', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='lightblue')
        ax.add_collection(collection)
    
    def plot_tcells(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.tcell_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='pink', alpha=1) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='pink')
        ax.add_collection(collection)
    
    def plot_mets(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.met_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='red', alpha=1) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='red')
        ax.add_collection(collection)    

    def plot_neutrophils(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.neutrophil_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='darkblue', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='darkblue')
        ax.add_collection(collection)

    def plot_fibroblasts(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.fibroblast_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='yellow', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='yellow')
        ax.add_collection(collection)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num=0, timepoint=0, *, config=None):
        if config is None: config = LiverMetTimepointPlotterV2.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.margins(0)
        ax.set_title(f'{simulation_timepoint.name} {simulation_timepoint.id}')

        LiverMetTimepointPlotterV2.plot_background(fig, ax, simulation_timepoint)
        LiverMetTimepointPlotterV2.plot_tcells(fig, ax, simulation_timepoint)
        LiverMetTimepointPlotterV2.plot_fibroblasts(fig, ax, simulation_timepoint)
        LiverMetTimepointPlotterV2.plot_mets(fig, ax, simulation_timepoint)
        LiverMetTimepointPlotterV2.plot_neutrophils(fig, ax, simulation_timepoint)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

class MacrophageTimepointPlotterV2:
    @dataclasses.dataclass
    class Config:
        ylim:tuple[int]=None
        xlim:tuple[int]=None
        phenotype_colorbar:bool=True
        background='lightblue'

    def plot_macrophages(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, *, config:Config=None):
        data = simulation_timepoint.macrophages_data
        norm = matplotlib.colors.Normalize(vmin=0.0, vmax=1)
        cmap = truncate_colormap('summer_r', 0.0, 1.0)
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc=cmap(norm(cell.phenotype))) for _, cell in data.iterrows()],
            edgecolors='none', facecolors=cmap(norm(data.phenotype.to_numpy())))
        ax.add_collection(collection)
        if config is not None and config.phenotype_colorbar:
            cbar = fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label='Macrophage Phenotype', ticks=[0,1])
            cbar.ax.set_yticklabels(['M1', 'M2'])


    def plot_stroma(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='lightblue', alpha=0.5) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='lightblue')
        ax.add_collection(collection)

    def plot_tumour(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, *, sim=None):
        data = simulation_timepoint.tumour_data
        patches = []
        colors = []
        for _, cell in data.iterrows():
            a = 0.01 if sim is None else sim.parameters['TumourNecroticConcentration']
            b = 0.01 if sim is None else sim.parameters['TumourHypoxicConcentration']
            if cell.oxygen <= a:
                # necrotic
                c = 'white'
            elif cell.oxygen <= b:
                # hypoxic
                c = 'darkorchid'
            else:
                #healthy
                c = 'purple'
            patches.append(matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='black', fc=c))
            colors.append(matplotlib.colors.to_rgba(c))
        collection = matplotlib.collections.PatchCollection(patches, edgecolors=np.array(colors), facecolors=np.array(colors))
        #collection.set_facecolors(np.array(colors))
        ax.add_collection(collection)

    def plot_blood_vessels(fig:plt.Figure, ax:plt.Axes, simulation_timepoint):
        data = simulation_timepoint.blood_vessel_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc='red') for _, cell in data.iterrows()],
            edgecolors='none', facecolors='red')
        ax.add_collection(collection)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = MacrophageTimepointPlotterV2.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor(config.background)
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        
        MacrophageTimepointPlotterV2.plot_stroma(fig, ax, simulation_timepoint)
        MacrophageTimepointPlotterV2.plot_macrophages(fig, ax, simulation_timepoint, config=config)
        MacrophageTimepointPlotterV2.plot_tumour(fig, ax, simulation_timepoint, sim=sim)
        MacrophageTimepointPlotterV2.plot_blood_vessels(fig, ax, simulation_timepoint)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')
