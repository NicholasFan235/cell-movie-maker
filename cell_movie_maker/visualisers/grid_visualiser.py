
from ..simulation import Simulation
from ..plotters import TimepointPlotter
# from .timepoint_plotter import TimepointPlotter
# from .timepoint_plotter_v2 import TimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging


class GridVisualiser:
    def __init__(self, simulation_folder_grid, output_parent_folder = 'visualisations'):
        self.results_folder_grid = [[
            os.path.join(sim_folder, 'results_from_time_0')
            for sim_folder in sim_folders] for sim_folders in simulation_folder_grid]
        self.simulation_grid = [[Simulation(f) for f in fs] for fs in self.results_folder_grid]

        self.sim_ids = [[
            os.path.basename(os.path.dirname(f))
            for f in fs] for fs in self.results_folder_grid]
        self.sim_name = os.path.basename(os.path.dirname(simulation_folder_grid[0][0]))

        self.shape = (len(simulation_folder_grid), len(simulation_folder_grid[0]))

        if (not os.path.exists(output_parent_folder)):
            pathlib.Path(output_parent_folder).mkdir(exist_ok=True)
        self.output_folder = os.path.join(output_parent_folder, self.sim_name)
        if not os.path.exists(self.output_folder):
            pathlib.Path(self.output_folder).mkdir(exist_ok=True)

        self.figsize = (8,8)
        self.dpi = 100
        self.postprocess_grid = None

        self.plotter_config = TimepointPlotter.Config()
        self.plotter = TimepointPlotter

        
    def post_frame(self, frame_num:int, timepoint:int, fig, ax):
        fig.savefig(os.path.join(self.output_folder_grid, 'frame_{}.png'.format(frame_num)), dpi=self.dpi, facecolor='white', transparent=False)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        fig, axs = plt.subplots(self.shape[0],self.shape[1],figsize=(self.shape[1]*self.figsize[0],self.shape[0]*self.figsize[1]),
                                gridspec_kw=dict(hspace=0, wspace=0))
        #fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)
        #fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
        fig.tight_layout()

        for i,(_simulations, _ids) in enumerate(zip(self.simulation_grid, self.sim_ids)):
            for j,(simulation, sim_id) in enumerate(zip(_simulations, _ids)):
                simulation_timepoint = simulation.read_timepoint(timepoint)
                if len(axs.shape)==1:
                    self.plotter.plot(fig, axs[i+j], simulation_timepoint, frame_num, simulation_timepoint.timestep, sim=simulation, config=self.plotter_config)
                else:
                    self.plotter.plot(fig, axs[i][j], simulation_timepoint, frame_num, simulation_timepoint.timestep, sim=simulation, config=self.plotter_config)

        if self.postprocess_grid is not None:
            self.postprocess_grid(fig, axs)

        return fig, axs
    
    def _visualise_frame(self, info:tuple[int,int]):
        try:
            fig, ax = self.visualise_frame(*info)
            if fig is not None:
                self.post_frame(*info, fig, ax)
                plt.close(fig)
        except Exception as e:
            logging.error(f'Error processing frame #{info[1]}: {e}')
            raise e

    def create_output_folder(self, name='grid', *, clean_dir=False):
        self.output_folder_grid = os.path.join(self.output_folder, name)
        if os.path.exists(self.output_folder_grid) and clean_dir:
            shutil.rmtree(self.output_folder_grid)
        if not os.path.exists(self.output_folder_grid):
            pathlib.Path(self.output_folder_grid).mkdir(exist_ok=True)

    def visualise(self, name='grid', start=0, stop=None, step=1,
                  postprocess=None, clean_dir=True, cmap=False, auto_execute=True, disable_tqdm=False):
        self.postprocess_grid = postprocess

        if auto_execute:
            self.simulation_grid[0][0].for_timepoint(self._visualise_frame, start=start, stop=stop, step=step, disable_tqdm=disable_tqdm)
        
