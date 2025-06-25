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


# class MacrophageCountPlotter:
#     @dataclasses.dataclass
#     class Config:
#         output_parent_folder:pathlib.Path|str|None=None
#         cache:bool=False

#     def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
#         if config is None: config = MacrophageCountPlotter.Config()
#         info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

#         ax.set_title('N Macrophages')
#         ax.fill_between(info.index/60/24, info['n_tumour'], color='purple', label='Healthy')
#         ax.fill_between(info.index/60/24, info['n_tumour_hypoxic'], color='mediumpurple', label='Hypoxic')
#         ax.fill_between(info.index/60/24, info['n_tumour_necrotic'], color='white', label='Necrotic')
#         ax.legend(loc='upper left')
#         ax.plot(info.index/60/24, info['n_tumour'], '-k')
#         ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
#         ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
#         #ax.set_ylabel('N Cells')
#         ax.set_xlabel('Time /days')


class MacrophagePhenotypeCountPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
        cache:bool=False
        phenotype_cmap = matplotlib.colormaps['summer_r']
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = MacrophagePhenotypeCountPlotter.Config()
        info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

        ax.set_title('Macrophage Phenotype')
        cmap = config.phenotype_cmap
        ax.fill_between(info.index/60/24, info['n_macrophages'], color=cmap(1.0), label='P=1')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.9'], color=cmap(0.9), label='P<=.9')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.8'], color=cmap(0.8), label='P<=.8')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.7'], color=cmap(0.7), label='P<=.7')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.6'], color=cmap(0.6), label='P<=.6')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.5'], color=cmap(0.5), label='P<=.5')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.4'], color=cmap(0.4), label='P<=.4')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.3'], color=cmap(0.3), label='P<=.3')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.2'], color=cmap(0.2), label='P<=.2')
        # ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.1'], color=cmap(0.1), label='P<=.1')
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0.0'], color=cmap(0.0), label='P=0')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_macrophages'], '-k')
        if simulation_timepoint is not None:
            ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_macrophages'], 'ro')
            ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_macrophages'], info['n_macrophages'].max()])
        ax.set_xlabel('Time /days')

class MacrophagePhenotypeHistogramPlotter:
    @dataclasses.dataclass
    class Config:
        bins:int=10
        log_counts:bool=True
        phenotype_cmap = matplotlib.colormaps['summer_r']
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = MacrophagePhenotypeHistogramPlotter.Config()

        ax.set_title('Phenotype Distribution')
        ax.hist(simulation_timepoint.macrophage_data.phenotype, bins=config.bins, range=(0,1), log=config.log_counts)
        ax.set_xscale('linear')
        ax.invert_xaxis()
        ax.set_xlabel('Macrophage Phenotype')
