
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter, HistogramPlotter, TumourTimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2, TumourTimepointPlotterV2, PressureTimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np

class AbstractSimulationVisualiser:
    def __init__(self, simulation:Simulation, output_parent_folder = 'visualisations', visualisation_name = 'abstract'):
        self.sim = simulation
        self.visualisation_name = visualisation_name
        
        if (not os.path.exists(output_parent_folder)):
            os.mkdir(output_parent_folder)
        if (not os.path.exists(os.path.join(output_parent_folder, self.sim.name))):
            os.mkdir(os.path.join(output_parent_folder, self.sim.name))
        self.output_folder = os.path.join(output_parent_folder, self.sim.name, self.sim.id)
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)
        
    def visualise_frame(self, info):
        raise NotImplementedError()
    
    def visualise(self, start=0, stop=None, step=1, postprocess=None, clean_dir=True):
        self.output_folder = os.path.join(self.output_folder, self.visualisation_name)
        if os.path.exists(self.output_folder) and clean_dir:
            shutil.rmtree(self.output_folder)
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)

        self.postprocess = postprocess

        self.start = start
        self.stop = stop
        self.step = step

class SimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        #ax.margins(0.01)
        fig.tight_layout()
        self.tp.plot(fig, ax, simulation_timepoint, frame_num, timepoint)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, auto_execute=True, maxproc=64, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True
        self.tp = TimepointPlotterV2()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc)


class TumourSimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard_tumour', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        #ax.margins(0.01)
        fig.tight_layout()
        self.tp.plot(fig, ax, simulation_timepoint, frame_num, timepoint)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, auto_execute=True, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TumourTimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True
        self.tp = TumourTimepointPlotterV2()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)


class HistogramVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='histogram', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("AB;AC", figsize=(16,8))
        self.tp.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)
        self.hp.cytotoxic_histogram(fig, axs['B'], simulation_timepoint)
        self.hp.tumour_histogram(fig, axs['C'], simulation_timepoint)

        if self.postprocess is not None:
            self.postprocess(fig, axs)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return


    def visualise(self, auto_execute=True, *args, **kwargs):
        super().visualise(*args, **kwargs)
        
        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap = True
        self.tp = TimepointPlotterV2()

        self.hp = HistogramPlotter()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)
        #self.sim.for_final_timepoint(self.visualise_frame)

class ChemokineVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        data = simulation_timepoint.read_pde(self.chemokine_name)
        fig, ax = plt.subplots(1,1, figsize=(8,8))

        #ax.margins(0.01)
        fig.tight_layout()
        pos = ax.imshow(data, cmap=self.chemokine_cmap, vmin=data.min(), vmax=data.max(), **self.chemokine_kwargs)
        fig.colorbar(pos, ax=ax)

        if self.postprocess is not None:
            self.postprocess(fig, ax, data=data)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, chemokine_cmap='jet', chemokine_kwargs={}, auto_execute=True, *args, **kwargs):
        super().visualise(*args, **kwargs)

        self.chemokine_name = self.visualisation_name
        self.chemokine_cmap = chemokine_cmap
        self.chemokine_kwargs = chemokine_kwargs
        
        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)

class PressureVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='pressure', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        #ax.margins(0.01)
        fig.tight_layout()
        self.tp.plot(fig, ax, simulation_timepoint, frame_num, timepoint)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, auto_execute=True, *args, **kwargs):
        super().visualise(*args, **kwargs)

        self.tp = PressureTimepointPlotterV2()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step)
