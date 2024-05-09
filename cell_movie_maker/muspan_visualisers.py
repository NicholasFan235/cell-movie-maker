from .simulation import Simulation
from .simulation_visualiser import AbstractSimulationVisualiser
from .timepoint_plotter import TimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2
from .muspan_plotter import MuspanPCFPlotter, MuspanWeightedPCFPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import muspan as ms


class AbstractMuspanVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='abstract_muspan', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.muspan_pcf_config = MuspanPCFPlotter.Config()

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        tp = self.sim.read_timepoint(timepoint)
        tp.data['tmp'] = tp.data.cell_type
        tp.data.loc[(tp.data.cell_type=='Tumour') & (tp.data.damage > 1), 'tmp'] = 'Dead Tumour'
        pc = ms.pointcloud.generatePointCloud('Test',tp.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', tp.data.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', tp.data.potency.to_numpy())
        pc.addLabels('damage', 'continuous', tp.data.damage.to_numpy())

        return self.visualise_frame_muspan(frame_num, timepoint, tp, pc)
    
    def visualise_frame_muspan(self, frame_num:int, timepoint:int, tp, pc)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        raise NotImplementedError
    
    def visualise(self, *args, **kwargs):
        super().visualise(*args, **kwargs)


class MuspanPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='pcf', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
    
    def visualise_frame_muspan(self, frame_num:int, timepoint:int, tp, pc)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AAB;AAC;AAD", figsize=(16,12))
        fig.tight_layout()
        TimepointPlotterV2.plot(fig, axs['A'], tp, frame_num, timepoint)
        MuspanPCFPlotter.plot_tcell_tcell_pcf(fig, axs['B'], pc, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_tcell_tumour_pcf(fig, axs['C'], pc, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_tumour_tumour_pcf(fig, axs['D'], pc, config=self.muspan_pcf_config)

        if self.postprocess is not None:
            self.postprocess(fig, axs)

        return fig, axs

    def visualise(self, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True

        #self.sim.for_final_timepoint(self.visualise_frame)
        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)

class MuspanWeightedPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='w_pcf', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        tp = self.sim.read_timepoint(timepoint)
        subset = tp.data[tp.data.cell_type.isin(['Tumour', 'T Cell', 'Blood Vessel'])]
        pc = ms.pointcloud.generatePointCloud('Test',subset[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', subset.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', subset.potency.to_numpy())
        pc.addLabels('damage', 'continuous', subset.damage.to_numpy())

        return self.visualise_frame_muspan(frame_num, timepoint, tp, pc)
    
    def visualise_frame_muspan(self, frame_num:int, timepoint:int, tp, pc)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AAB;AAC", figsize=(16,12))
        fig.tight_layout()
        TimepointPlotterV2.plot(fig, axs['A'], tp, frame_num, timepoint)
        MuspanPCFPlotter.plot_potency_tumour_pcf(fig, axs['B'], pc, config=self.muspan_pcf_config)
        MuspanPCFPlotter.plot_damage_tcell_pcf(fig, axs['C'], pc, config=self.muspan_pcf_config)
        
        if self.postprocess is not None:
            self.postprocess(fig, axs)
        
        return fig, axs
    
    def visualise(self, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True

        #self.sim.for_final_timepoint(self.visualise_frame)
        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)

