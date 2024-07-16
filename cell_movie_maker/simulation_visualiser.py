
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter, HistogramPlotter, TumourTimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2, TumourTimepointPlotterV2, PressureTimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging


class AbstractSimulationVisualiser:
    def __init__(self, simulation:Simulation, output_parent_folder = 'visualisations', visualisation_name = 'abstract'):
        self.sim = simulation
        self.visualisation_name = visualisation_name
        self.figsize = (8,8)
        self.postprocess = None
        
        if (not os.path.exists(output_parent_folder)):
            pathlib.Path(output_parent_folder).mkdir(exist_ok=True)
        if (not os.path.exists(os.path.join(output_parent_folder, self.sim.name))):
            pathlib.Path(os.path.join(output_parent_folder, self.sim.name)).mkdir(exist_ok=True)
        self.output_folder = os.path.join(output_parent_folder, self.sim.name, self.sim.id)
        if not os.path.exists(self.output_folder):
            pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        
    def post_frame(self, frame_num:int, timestep:int, fig:plt.Figure, ax:plt.Axes|np.ndarray[plt.Axes]):
        fig.savefig(os.path.join(self.output_folder, self.visualisation_name, 'frame_{}.png'.format(frame_num)))

    def visualise_frame(self, frame_num:int, timestep:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        raise NotImplementedError()
    
    def _visualise_frame(self, args:tuple[int,int]):
        try:
            fig, ax = self.visualise_frame(*args)
            if fig is not None:
                self.post_frame(*args, fig, ax)
                plt.close(fig)
        except Exception as e:
            logging.error(f'Error processing frame #{args[1]}: {e}')
            raise e

    def visualise(self, start=0, stop=None, step=1, postprocess=None, clean_dir=True):
        self.create_output_folder(clean_dir=clean_dir)
        if postprocess is not None:
            self.postprocess = postprocess

        self.start = start
        self.stop = stop
        self.step = step
    
    def create_output_folder(self, *, clean_dir:bool):
        output_folder = os.path.join(self.output_folder, self.visualisation_name)
        if os.path.exists(output_folder) and clean_dir:
            shutil.rmtree(output_folder)
        if not os.path.exists(output_folder):
            pathlib.Path(output_folder).mkdir(exist_ok=True)

class SimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.plotter_config = TimepointPlotterV2.Config()

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        TimepointPlotterV2.plot(fig, ax, simulation_timepoint, frame_num, timepoint, config=self.plotter_config)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        return fig, ax

    def visualise(self, auto_execute=True, maxproc=64, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True

        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc, disable_tqdm=disable_tqdm)


class TumourSimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard_tumour', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.tumour_plotter_config = TumourTimepointPlotterV2.Config()

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        TumourTimepointPlotterV2.plot(fig, ax, simulation_timepoint, frame_num, timepoint, sim=self.sim, config=self.tumour_plotter_config)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        return fig, ax

    def visualise(self, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TumourTimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True

        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)


class HistogramVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='histogram', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.histogram_plotter_config = HistogramPlotter.Config()
        self.plotter_config = TimepointPlotterV2.Config()

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("AB;AC", figsize=self.figsize)
        TimepointPlotterV2.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint, config=self.plotter_config)
        HistogramPlotter.cytotoxic_histogram(fig, axs['B'], simulation_timepoint, config=self.histogram_plotter_config)
        HistogramPlotter.tumour_histogram(fig, axs['C'], simulation_timepoint, config=self.histogram_plotter_config)

        if self.postprocess is not None:
            self.postprocess(fig, axs)

        return fig, axs


    def visualise(self, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)
        
        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap = True

        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)
        #self.sim.for_final_timepoint(self.visualise_frame)

class ChemokineVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        data = simulation_timepoint.read_pde(self.chemokine_name)
        fig, ax = plt.subplots(1,1, figsize=self.figsize)

        #ax.margins(0.01)
        fig.tight_layout()
        pos = ax.imshow(data, cmap=self.chemokine_cmap, vmin=0, vmax=max(data.max(),1.0), **self.chemokine_kwargs)
        fig.colorbar(pos, ax=ax)

        if self.postprocess is not None:
            self.postprocess(fig, ax, data=data)

        return fig, ax

    def visualise(self, chemokine_cmap='jet', chemokine_kwargs={}, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        self.chemokine_name = self.visualisation_name
        self.chemokine_cmap = chemokine_cmap
        self.chemokine_kwargs = chemokine_kwargs
        
        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)

class PressureVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='pressure', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.pressure_plotter_config = PressureTimepointPlotterV2.Config()

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        PressureTimepointPlotterV2.plot(fig, ax, simulation_timepoint, frame_num, timepoint, config=self.pressure_plotter_config)

        if self.postprocess is not None:
            self.postprocess(fig, ax)

        return fig, ax

    def visualise(self, auto_execute=True, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, disable_tqdm=disable_tqdm)
