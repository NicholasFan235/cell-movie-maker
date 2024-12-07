from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ..simulation_visualiser import AbstractSimulationVisualiser
from ..plotters import TimepointPlotter
from ..plotters.legacy_plotters.muspan_plotter import MuspanPCFPlotter, MuspanWeightedPCFPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import muspan as ms


class AbstractMuspanVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='abstract_muspan', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.muspan_pcf_config = MuspanPCFPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        tp.data['tmp'] = tp.data.cell_type
        tp.data.loc[(tp.data.cell_type=='Tumour') & (tp.data.damage > 1), 'tmp'] = 'Dead Tumour'
        pc = ms.pointcloud.generatePointCloud('Test',tp.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', tp.data.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', tp.data.potency.to_numpy())
        pc.addLabels('damage', 'continuous', tp.data.damage.to_numpy())

        return self.visualise_frame_muspan(sim, tp, pc, frame_num)
    
    def visualise_frame_muspan(self, sim:Simulation, tp:SimulationTimepoint, domain, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        raise NotImplementedError


class MuspanPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, visualisation_name='pcf', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()
    
    def visualise_frame_muspan(self, sim:Simulation, tp:SimulationTimepoint, domain, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AAB;AAC;AAD", figsize=(16,12))
        fig.tight_layout()
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)
        MuspanPCFPlotter.plot_tcell_tcell_pcf(fig, axs['B'], domain, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_tcell_tumour_pcf(fig, axs['C'], domain, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_tumour_tumour_pcf(fig, axs['D'], domain, config=self.muspan_pcf_config)
        return fig, axs


class MuspanWeightedPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, visualisation_name='w_pcf', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        subset = tp.data[tp.data.cell_type.isin(['Tumour', 'T Cell', 'Blood Vessel'])]
        pc = ms.pointcloud.generatePointCloud('Test',subset[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', subset.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', subset.potency.to_numpy())
        pc.addLabels('damage', 'continuous', subset.damage.to_numpy())

        return self.visualise_frame_muspan(sim, tp, pc, frame_num)
    
    def visualise_frame_muspan(self, sim:Simulation, tp:SimulationTimepoint, domain, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AAB;AAC", figsize=(16,12))
        fig.tight_layout()
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)
        MuspanPCFPlotter.plot_potency_tumour_pcf(fig, axs['B'], domain, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_damage_tcell_pcf(fig, axs['C'], domain, config=self.muspan_pcf_config)
        return fig, axs
    
