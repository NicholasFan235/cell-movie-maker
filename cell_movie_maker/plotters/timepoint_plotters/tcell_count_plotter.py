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
        ax.fill_between(info.index/60/24, info['n_tcells'], color=cmap(0.99), label='0% Exhausted')
        ax.fill_between(info.index/60/24, info['n_tcells_potency_le90'], color=cmap(0.8), label='10% Exhausted')
        ax.fill_between(info.index/60/24, info['n_tcells_potency_le80'], color=cmap(0.6), label='20% Exhausted')
        ax.fill_between(info.index/60/24, info['n_tcells_potency_le60'], color=cmap(0.4), label='40% Exhausted')
        ax.fill_between(info.index/60/24, info['n_tcells_potency_le20'], color=cmap(0.2), label='80% Exhausted')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tcells'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tcells'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tcells'], info['n_tcells'].max()])
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

class TCellTumourStackedRegionCountPlotter:
    @dataclasses.dataclass
    class Config:
        alpha=1
        analysis_alpha=.5
        buffer=5
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellTumourRegionCountPlotter.Config()

        assert Config.simulation_database is not None, "No simulation database set in config"
        import chaste_simulation_database_connector as csdc
        collector = Config.simulation_database.CollectorFactory(csdc.collectors.TumourRegionTCellCountCollector)
        region_counts = collector.collect_simulation(simulation_timepoint.name, int(simulation_timepoint.id.lstrip('sim_')))

        ax.set_title('TCells')
        ax.fill_between(
            region_counts.index.get_level_values('timestep')/60/24,
            y1=region_counts.necrotic_region_count,
            y2=0,
            color='lightgray', label='Necrotic', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_counts.index.get_level_values('timestep')/60/24,
            y1=region_counts.necrotic_region_count + region_counts.hypoxic_region_count,
            y2=region_counts.necrotic_region_count,
            color='mediumpurple', label='Hypoxic', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_counts.index.get_level_values('timestep')/60/24,
            y1=region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count,
            y2=region_counts.necrotic_region_count + region_counts.hypoxic_region_count,
            color='purple', label='Normoxic', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_counts.index.get_level_values('timestep')/60/24,
            y1=region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count + region_counts.buffer_region_count,
            y2=region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count,
            color='blue', label='Boundary', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_counts.index.get_level_values('timestep')/60/24,
            y1=region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count + region_counts.buffer_region_count + region_counts.exterior_region_count,
            y2=region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count + region_counts.buffer_region_count,
            color='red', label='Distant', alpha=config.alpha, linewidth=0)
        ax.plot(region_counts.index.get_level_values('timestep')/60/24,
                region_counts.necrotic_region_count + region_counts.hypoxic_region_count + region_counts.normoxic_region_count + region_counts.buffer_region_count + region_counts.exterior_region_count,
                'k-')
        ax.axvline(simulation_timepoint.timestep/60/24,0,1, linestyle='dashed', color='red')
        ax.legend()
        ax.set_xlabel('time (days)')
        ax.set_ylabel('N T-Cells')
        ax.set_xlim(0,None)
        ax.set_ylim(0,None)

class TCellTumourRegionCountPlotter:
    @dataclasses.dataclass
    class Config:
        alpha=1
        analysis_alpha=.5
        analysis_buffer=5
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellTumourRegionDensityPlotter.Config()

        assert Config.simulation_database is not None, "No simulation database set in config"
        import chaste_simulation_database_connector as csdc
        collector = Config.simulation_database.CollectorFactory(csdc.collectors.TumourRegionTCellCountCollector)
        region_counts = collector.collect_simulation(simulation_timepoint.name, int(simulation_timepoint.id.lstrip('sim_')))

        ax.set_title('TCells')
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.necrotic_region_count,
            color='black', label='Necrotic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.hypoxic_region_count,
            color='mediumpurple', label='Hypoxic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.normoxic_region_count,
            color='purple', label='Normoxic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.buffer_region_count,
            color='blue', label='Boundary', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.exterior_region_count,
            color='red', label='Distant', alpha=1)
        ax.axvline(simulation_timepoint.timestep/60/24,0,1, linestyle='dashed', color='red')
        ax.legend()
        ax.set_xlabel('time (days)')
        ax.set_ylabel('N T-Cells')
        ax.set_xlim(0,None)
        ax.set_ylim(0,None)

class TCellTumourRegionDensityPlotter:
    @dataclasses.dataclass
    class Config:
        alpha=1
        analysis_alpha=.5
        analysis_buffer=5
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim=None, config:Config=None):
        if config is None: config = TCellTumourRegionDensityPlotter.Config()

        assert Config.simulation_database is not None, "No simulation database set in config"
        import chaste_simulation_database_connector as csdc
        collector = Config.simulation_database.CollectorFactory(csdc.collectors.TumourRegionTCellCountCollector)
        region_counts = collector.collect_simulation(simulation_timepoint.name, int(simulation_timepoint.id.lstrip('sim_')))

        ax.set_title('TCells')
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.necrotic_region_density,
            color='black', label='Necrotic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.hypoxic_region_density,
            color='mediumpurple', label='Hypoxic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.normoxic_region_density,
            color='purple', label='Normoxic', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.buffer_region_density,
            color='blue', label='Boundary', alpha=1)
        ax.plot(
            region_counts.index.get_level_values('timestep')/60/24,
            region_counts.exterior_region_density,
            color='red', label='Distant', alpha=1)
        ax.axvline(simulation_timepoint.timestep/60/24,0,1, linestyle='dashed', color='red')
        ax.legend()
        ax.set_xlabel('time (days)')
        ax.set_ylabel('T-Cell Density')
        ax.set_xlim(0,None)
        ax.set_ylim(0,None)