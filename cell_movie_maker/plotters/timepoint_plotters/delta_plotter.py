import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.colors
import matplotlib.cm
import matplotlib.pyplot as plt
import dataclasses
from ..helpers import truncate_colormap
from ...analysers import DeltaAnalyser
from ...analysers.helpers import alpha_shape


class DamageDeltaTimepointPlotter:
    @dataclasses.dataclass
    class Config:
        ylim:tuple[int]=None
        xlim:tuple[int]=None
        delta:float=24*60
        damage_cm=matplotlib.cm.ScalarMappable(cmap=truncate_colormap(matplotlib.colormaps['hot_r'], 0.05, 1),
            norm = matplotlib.colors.Normalize(vmin=0, vmax=1))

    def plot_tumour(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, config:Config):
        data = simulation_timepoint.tumour_data.set_index('cell_id').join(DeltaAnalyser(config.delta).analyse(simulation_timepoint, simulation_timepoint.sim).set_index('cell_id'), how='left')
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius*.7) for _, cell in data.iterrows()],
            edgecolors=None, facecolors = config.damage_cm.to_rgba(data.delta_damage.fillna(0).to_numpy()))
        collection.set_rasterized(True)
        ax.add_collection(collection)

    def plot_cytotoxic(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, config:Config):
        data = simulation_timepoint.cytotoxic_data
        if len(data) <= 0: return
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius) for _, cell in data.iterrows()],
            edgecolors=None, facecolors='orange', alpha=0.2)
        collection.set_rasterized(True)
        ax.add_collection(collection)
        
    def plot_blood_vessels(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, config:Config):
        data = simulation_timepoint.blood_vessel_data
        collection = matplotlib.collections.PatchCollection(
            [matplotlib.patches.Circle((cell.x, cell.y), cell.radius) for _, cell in data.iterrows()],
            edgecolors='none', facecolors='red', alpha=.2)
        collection.set_rasterized(True)
        ax.add_collection(collection)
    
    def plot_boundary(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, config:Config):
        import shapely
        shape = alpha_shape(simulation_timepoint.tumour_data[['x','y']].to_numpy(), alpha=0.5)[0]
        if isinstance(shape, shapely.Polygon):
            ax.add_patch(matplotlib.patches.Polygon(list(zip(*shape.exterior.xy)), fill=False, ec='black'))
        if isinstance(shape, shapely.MultiPolygon):
            for p in shape.geoms:
                ax.add_patch(matplotlib.patches.Polygon(list(zip(*p.exterior.xy)), fill=False, ec='black'))


    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num:int, timepoint:int, *, sim=None, config:Config=None):
        if config is None: config = DamageDeltaTimepointPlotter.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.id}')
        DamageDeltaTimepointPlotter.plot_blood_vessels(fig, ax, simulation_timepoint, config)
        DamageDeltaTimepointPlotter.plot_cytotoxic(fig, ax, simulation_timepoint, config)
        DamageDeltaTimepointPlotter.plot_tumour(fig, ax, simulation_timepoint, config)
        DamageDeltaTimepointPlotter.plot_boundary(fig, ax, simulation_timepoint, config)
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

