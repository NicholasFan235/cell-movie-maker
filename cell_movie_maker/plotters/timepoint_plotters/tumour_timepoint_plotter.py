import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses


class TumourTimepointPlotter:
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
        if config is None: config = TumourTimepointPlotter.Config()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f'{float(timepoint)/60/24:.1f} days')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}')
        TumourTimepointPlotter.plot_stroma(fig, ax, simulation_timepoint)
        TumourTimepointPlotter.plot_tumour(fig, ax, simulation_timepoint, sim=sim)
        TumourTimepointPlotter.plot_blood_vessels(fig, ax, simulation_timepoint)
        ax.relim()
        ax.set_ylim(*(config.ylim if config.ylim is not None else (0, sim.parameters['HEIGHT']) if sim is not None else (simulation_timepoint.data.y.min(), simulation_timepoint.data.y.max())))
        ax.set_xlim(*(config.xlim if config.xlim is not None else (0, sim.parameters['WIDTH']) if sim is not None else (simulation_timepoint.data.x.min(), simulation_timepoint.data.x.max())))
        ax.set_aspect(1.0, adjustable='box')
