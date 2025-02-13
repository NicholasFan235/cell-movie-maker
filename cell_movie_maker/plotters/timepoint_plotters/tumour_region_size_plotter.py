import numpy as np
import matplotlib
import matplotlib.patches
import matplotlib.collections
import matplotlib.pyplot as plt
import dataclasses
import pathlib
import pandas as pd
from ...config import Config


class TumourRegionSizePlotter:
    @dataclasses.dataclass
    class Config:
        alpha=1
        analysis_alpha=.5
    
    def plot(fig:plt.Figure, ax:plt.Axes, simulation_timepoint, frame_num, timepoint, *, sim, config:Config=None):
        if config is None: config = TumourRegionSizePlotter.Config()

        assert Config.simulation_database is not None, "No simulation database set in config"
        import chaste_simulation_database_connector as csdc
        collector = Config.simulation_database.CollectorFactory(csdc.collectors.TumourRegionSizeCollector)
        region_sizes = collector.collect_simulation(simulation_timepoint.name, int(simulation_timepoint.id.lstrip('sim_')))

        ax.set_title('Tumour Area')
        ax.fill_between(
            region_sizes.index.get_level_values('timestep')/60/24,
            y1=region_sizes['tumour_area'],
            y2=region_sizes.necrotic_area + region_sizes.hypoxic_area,
            color='purple', label='Normoxic', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_sizes.index.get_level_values('timestep')/60/24,
            y1=region_sizes['necrotic_area'] + region_sizes['hypoxic_area'],
            y2=region_sizes.necrotic_area,
            color='mediumpurp ',
            label='Hypoxic', alpha=config.alpha, linewidth=0)
        ax.fill_between(
            region_sizes.index.get_level_values('timestep')/60/24,
            y1=region_sizes['necrotic_area'],
            y2=0,
            color='lightgray', label='Necrotic', alpha=config.alpha, linewidth=0)
        ax.plot(region_sizes.index.get_level_values('timestep')/60/24,
                region_sizes.tumour_area, 'k-')
        ax.axvline(simulation_timepoint.timestep/60/24,0,1, linestyle='dashed', color='red')
        ax.legend()
        ax.set_xlabel('time (days)')
        ax.set_ylabel('Area')
        ax.set_xlim(0,None)
        ax.set_ylim(0,None)
