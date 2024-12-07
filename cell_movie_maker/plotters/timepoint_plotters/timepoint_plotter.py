import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses
from ..helpers import truncate_colormap


class TimepointPlotter:
    @dataclasses.dataclass
    class Config:
        p_max:float|None=None
        pressure_cmap:str|matplotlib.colors.LinearSegmentedColormap='cividis'
        draw_colorbar:bool=True
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
        TimepointPlotter.plot_stroma(fig, ax, simulation_timepoint)
        TimepointPlotter.plot_macrophages(fig, ax, simulation_timepoint)
        TimepointPlotter.plot_tumour(fig, ax, simulation_timepoint)
        TimepointPlotter.plot_blood_vessels(fig, ax, simulation_timepoint)
        TimepointPlotter.plot_cytotoxic(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')

