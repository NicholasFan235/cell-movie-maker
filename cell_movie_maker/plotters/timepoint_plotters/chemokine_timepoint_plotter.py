import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses


class ChemokineTimepointPlotter:
    @dataclasses.dataclass
    class Config:
        chemokine:str = 'oxygen'
        cmap:str|matplotlib.colors.LinearSegmentedColormap='jet'
        vmin:float = 0
        vmax:float =None
        ylim:tuple[int]=None
        xlim:tuple[int]=None
        add_colorbar:bool=True

    def plot_cells(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, *, config:Config):
        data = simulation_timepoint.data
        norm = matplotlib.colors.Normalize(vmin=config.vmin, vmax=max(data.max(), 1.0) if config.vmax is None else config.vmax)
        cmap = matplotlib.colormaps[config.cmap] if isinstance(config.cmap, str) else config.cmap
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius, ec='none', fc=cmap(norm(cell[config.chemokine])), alpha=0.8) for _, cell in data.iterrows()],
            edgecolors='none', facecolors=cmap(norm(data[config.chemokine].to_numpy())))
        ax.add_collection(collection)
        if config.add_colorbar: fig.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = ChemokineTimepointPlotter.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} {config.chemokine}')
        
        ChemokineTimepointPlotter.plot_cells(fig, ax, simulation_timepoint, config=config)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')



class ChemokinePDETimepointPlotter:
    @dataclasses.dataclass
    class Config:
        cmap:str|matplotlib.colors.LinearSegmentedColormap='jet'
        chemokine:str='oxygen'
        imshow_kwargs:dict=dataclasses.field(default_factory=dict)
        colorbar_kwargs:dict=dataclasses.field(default_factory=dict)
        vmin:float=0
        vmax:float|None=None
        add_colorbar:bool=True

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config=None):
        if config is None: config = ChemokinePDETimepointPlotter.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        data = simulation_timepoint.read_pde(config.chemokine)
        kwargs = dict(
            cmap=config.cmap,
            vmin=config.vmin,
            vmax=max(data.max(), 1.0) if config.vmax is None else config.vmax,
            origin='lower',
        ) | config.imshow_kwargs
        pos = ax.imshow(data, **kwargs)
        if config.add_colorbar: fig.colorbar(pos, ax=ax, **config.colorbar_kwargs)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} {config.chemokine}')

