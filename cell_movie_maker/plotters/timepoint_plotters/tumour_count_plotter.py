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


class TumourCountPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
        cache:bool=False

    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TumourCountPlotter.Config()
        info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

        ax.set_title('N-Tumour cells')
        ax.fill_between(info.index/60/24, info['n_tumour'], color='purple', label='Healthy')
        ax.fill_between(info.index/60/24, info['n_tumour_hypoxic'], color='mediumpurple', label='Hypoxic')
        ax.fill_between(info.index/60/24, info['n_tumour_necrotic'], color='lightgray', label='Necrotic')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        if simulation_timepoint is not None:
            ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
            ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')


class TumourDamageCountPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TumourCountPlotter.Config()
        info:pd.DataFrame = load_info(sim, output_folder=config.output_parent_folder, cache=config.cache)

        ax.set_title('N-Tumour cells')
        cmap = plt.get_cmap('Purples')
        ax.fill_between(info.index/60/24, info['n_tumour'], color=cmap(0.99), label='0% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage_gt10'], color=cmap(0.8), label='10% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage_gt20'], color=cmap(0.6), label='20% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage_gt40'], color=cmap(0.4), label='60% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage_gt80'], color=cmap(0.2), label='80% Damaged')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        if simulation_timepoint is not None:
            if simulation_timepoint.timestep in info.index:
                ax.axvline(simulation_timepoint.timestep/60/24, linestyle='dashed', color='dimgray', lw=1)
                ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'o', color='dimgray', markersize=4)
                ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')


class TumourDamageHistogramPlotter:
    @dataclasses.dataclass
    class Config:
        output_parent_folder:pathlib.Path|str|None=None
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TumourDamageHistogramPlotter.Config()
        
        ax.set_title('Tumour Damage Distribution')
        ax.hist(simulation_timepoint.tumour_data.damage, bins=10, range=(0,1), log=True)
        ax.set_xscale('linear')
        ax.set_xlabel('Tumour Damage')

