from .simulation import Simulation
from .simulation_visualizer import AbstractSimulationVisualiser
from .timepoint_plotter import TimepointPlotter
from .muspan_plotter import MuspanPCFPlotter, MuspanWeightedPCFPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np

import sys
sys.path.append('/home/linc4121/Code/projects/MuSpAn')
import MuSpAn as ms


class AbstractMuspanVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='abstract_muspan', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        _, timepoint = info
        tp = self.sim.read_timepoint(timepoint)
        pc = ms.pointcloud.generatePointCloud('Test',tp.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', tp.data.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', tp.data.potency.to_numpy())
        pc.addLabels('damage', 'continuous', tp.data.damage.to_numpy())

        self.visualise_frame_muspan(info, tp, pc)
    
    def visualise_frame_muspan(self, info, tp, pc):
        raise NotImplementedError
    
    def visualise(self, *args, **kwargs):
        super().visualise(*args, **kwargs)


class MuspanPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='pcf', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
    
    def visualise_frame_muspan(self, info, tp, pc):
        frame_num, timepoint = info

        fig, axs = plt.subplot_mosaic("AAB;AAC;AAD", figsize=(16,12))
        self.tp.plot(axs['A'], tp, frame_num, timepoint)
        self.mp.plot_tcell_tcell_pcf(axs['B'], pc)
        self.mp.plot_tcell_tumour_pcf(axs['C'], pc)
        self.mp.plot_tumour_tumour_pcf(axs['D'], pc)

        if self.postprocess is not None:
            self.postprocess(fig, axs)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, *args, **kwargs):
        super().visualise(*args, **kwargs)

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.tp.cmap=True

        self.mp = MuspanPCFPlotter()

        #self.sim.for_final_timepoint(self.visualise_frame)
        self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)

class MuspanWeightedPCFVisualiser(AbstractMuspanVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='w_pcf', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        _, timepoint = info
        tp = self.sim.read_timepoint(timepoint)
        subset = tp.data[tp.data.cell_type.isin(['Tumour', 'T Cell'])]
        pc = ms.pointcloud.generatePointCloud('Test',subset[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', subset.cell_type.to_numpy())
        pc.addLabels('potency', 'continuous', subset.potency.to_numpy())
        pc.addLabels('damage', 'continuous', subset.damage.to_numpy())

        self.visualise_frame_muspan(info, tp, pc)
    
    def visualise_frame_muspan(self, info, tp, pc):
        frame_num, timepoint = info

        fig, axs = plt.subplot_mosaic("AAB;AAC", figsize=(16,12))
        self.tp.plot(axs['A'], tp, frame_num, timepoint)
        self.mp.plot_potency_tumour_pcf(axs['B'], pc)
        self.mp.plot_damage_tcell_pcf(axs['C'], pc)
        
        if self.postprocess is not None:
            self.postprocess(fig, axs)
        
        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return
    
    def visualise(self, *args, **kwargs):
        super().visualise(*args, **kwargs)

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.tp.cmap=True

        self.mp = MuspanWeightedPCFPlotter()

        self.sim.for_final_timepoint(self.visualise_frame)
        #self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)

