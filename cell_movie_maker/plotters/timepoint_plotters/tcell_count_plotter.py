import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses
import pathlib
import pandas as pd
from ...config import Config
from ..helpers import load_info


class TCellCountPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
        cache:bool=False

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellCountPlotter.Config()
        info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

        ax.set_title('N-Tumour cells')
        ax.fill_between(info.index/60/24, info['n_tumour'], color='purple', label='Healthy')
        ax.fill_between(info.index/60/24, info['n_tumour_hypoxic'], color='mediumpurple', label='Hypoxic')
        ax.fill_between(info.index/60/24, info['n_tumour_necrotic'], color='white', label='Necrotic')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')


class TCellExhaustionCountPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
        cache:bool=False
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellExhaustionCountPlotter.Config()
        info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

        ax.set_title('T-Cell Exhaustion')
        cmap = plt.get_cmap('Oranges')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.fill_between(info.index/60/24, info['n_t-cells'], color=cmap(0.99), label='0% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency90'], color=cmap(0.8), label='10% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency80'], color=cmap(0.6), label='20% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency60'], color=cmap(0.4), label='40% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency20'], color=cmap(0.2), label='80% Exhausted')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_t-cells'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_t-cells'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_t-cells'], info['n_t-cells'].max()])
        ax.set_xlabel('Time /days')

class TCellExhaustionHistogramPlotter:
    @dataclasses.dataclass
    class Config:
        bins:int=10
        log_counts:bool=True
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellExhaustionHistogramPlotter.Config()

        ax.set_title('Exhaustion Distribution')
        ax.hist(simulation_timepoint.cytotoxic_data.potency, bins=config.bins, range=(0,1), log=config.log_counts)
        ax.set_xscale('linear')
        ax.invert_xaxis()
        ax.set_xlabel('CD8+ Potency')

