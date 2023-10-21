from .svg_stitcher import SVGStitcher
import muspan as ms
from ..muspan_plotter import MuspanPCFPlotter, MuspanWeightedPCFPlotter, MuspanMacrophagePCFPlotter
import matplotlib.pylab as plt
import matplotlib as mpl
import os
import pathlib
import re
import tqdm
import multiprocessing
import pandas as pd
from ..simulation_timepoint import MacrophageSimulationTimepoint, SimulationTimepoint


class MacrophageSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='macrophages-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
        self.probe_vis_type = 'macrophage-svg-png'
        self.csf1_max = None
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def plot_csf1(self, fig, ax, simulation_timepoint):
        ax.set_title('CSF-1 (Chemoattractant)')
        ax.set_xticks([])
        ax.set_yticks([])
        csf1data = simulation_timepoint.csf1_data
        if csf1data is not None:
            csf1 = ax.imshow(csf1data, cmap='magma', vmin=0, vmax=self.csf1_max if self.csf1_max is not None else csf1data.max())
            fig.colorbar(csf1, ax=ax)

    def plot_macrophage_phenotype_count(self, fig, ax, simulation_timepoint):
        ax.set_title('N-Macrophages cells')
        cmap = plt.get_cmap('summer_r')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        #ax.fill_between(info.index/60/24, info['n_macrophages'], color=cmap(1))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype100'], color=cmap(0.99))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype80'], color=cmap(0.8))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype60'], color=cmap(0.6))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype40'], color=cmap(0.4))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype20'], color=cmap(0.2))
        ax.fill_between(info.index/60/24, info['n_macrophages_phenotype0'], color=cmap(0))
        
        #ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_macrophages'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_macrophages'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_macrophages'], info.n_macrophages.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')

    def plot_tumour_count(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('N-Tumour cells')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.fill_between(info.index/60/24, info['n_tumour'], color='lightpink')
        #ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')

    def read_pointcloud(self, simulation_timepoint):
        pc = ms.pointcloud.generatePointCloud('Test',simulation_timepoint.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', simulation_timepoint.data.cell_type.to_numpy())
        pc.addLabels('phenotype', 'continuous', simulation_timepoint.data.phenotype.to_numpy())
        return pc

    def run(self, *args, **kwargs):
        self.pcf_plotter = MuspanMacrophagePCFPlotter()
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)
        pc = self.read_pointcloud(simulation_timepoint, damage=False, potency=False)

        axs['A'].imshow(self.get_frame('macrophage-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        self.plot_csf1(fig, axs['D'], simulation_timepoint)
        self.plot_tumour_count(fig, axs['C'], simulation_timepoint)
        self.plot_macrophage_phenotype_count(fig, axs['E'], simulation_timepoint)

        #self.pcf_plotter.plot_macrophage_tumour_pcf(fig, axs['F'], pc)

        #self.plot_macrophage_tumour_pcf(fig, axs['F'], simulation_timepoint)
        #self.plot_macrophage_macrophage_pcf(fig, axs['G'], simulation_timepoint)
        self.post(fig, axs, n)