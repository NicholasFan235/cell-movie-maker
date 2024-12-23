import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses


class PressureTimepointPlotter:
    @dataclasses.dataclass
    class Config:
        p_max:float|None=None
        pressure_cmap:str|matplotlib.colors.LinearSegmentedColormap='cividis'
        draw_colorbar:bool=True
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
        if config is None: config = PressureTimepointPlotter.Config()

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num} Pressure')
        
        PressureTimepointPlotter.plot_cells(fig, ax, simulation_timepoint, config=config)

        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

