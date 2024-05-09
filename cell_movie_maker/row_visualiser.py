
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging


class RowVisualiser:
    def __init__(self, simulation_folder_grid, output_parent_folder = 'visualisations'):
        self.results_folder_grid = [
            os.path.join(sim_folder, 'results_from_time_0')
            for sim_folder in simulation_folder_grid]
        self.simulations = [Simulation(f) for f in self.results_folder_grid]

        self.sim_ids = [
            os.path.basename(os.path.dirname(f))
            for f in self.results_folder_grid]
        self.sim_name = os.path.basename(os.path.dirname(simulation_folder_grid[0]))

        self.n = len(simulation_folder_grid)

        if (not os.path.exists(output_parent_folder)):
            pathlib.Path(output_parent_folder).mkdir(exist_ok=True)
        self.output_folder = os.path.join(output_parent_folder, self.sim_name)
        if not os.path.exists(self.output_folder):
            pathlib.Path(self.output_folder).mkdir(exist_ok=True)

        self.postprocess_grid = None

    def post_frame(self, frame_num:int, timestep:int, fig:plt.Figure, ax:plt.Axes|np.ndarray[plt.Axes]):
        fig.savefig(os.path.join(self.output_folder_grid, f'frame_{frame_num}.png'))

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplots(1,self.n,figsize=(self.n*8, 8), facecolor='white')
        #fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)
        fig.tight_layout()

        for i,(simulation, sim_id) in enumerate(zip(self.simulations, self.sim_ids)):
            simulation_timepoint = simulation.read_timepoint(timepoint)
            if simulation_timepoint is not None:
                TimepointPlotterV2.plot(fig, axs[i], simulation_timepoint, frame_num, timepoint)
        for ax in axs:
            ax.margins(0.01)

        if self.postprocess_grid is not None:
            self.postprocess_grid(fig, axs)
        return fig, axs
    
    def _visualise_frame(self, info:tuple[int,int]):
        try:
            fig, ax = self.visualise_farme(*info)
            if fig is not None:
                self.post_frame(*info, fig, ax)
                plt.close(fig)
        except Exception as e:
            logging.error(f'Error processing frame #{info[1]}: e')
            raise e

    def visualise(self, name='grid', start=0, stop=None, step=1,
                  postprocess=None, clean_dir=True, cmap=False, auto_execute=True, disable_tqdm=False):
        self.create_output_folder(name, clean_dir=clean_dir)
        self.postprocess_grid = postprocess

        if auto_execute:
            self.simulations[0].for_timepoint(self._visualise_frame, start=start, stop=stop, step=step, disable_tqdm=disable_tqdm)
        
    def create_output_folder(self, name='grid', *, clean_dir:bool=False):
        self.output_folder_grid = os.path.join(self.output_folder, name)
        if os.path.exists(self.output_folder_grid) and clean_dir:
            shutil.rmtree(self.output_folder_grid)
        if not os.path.exists(self.output_folder_grid):
            pathlib.Path(self.output_folder_grid).mkdir(exist_ok=True)
