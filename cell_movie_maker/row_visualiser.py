
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib

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

    def visualise_frame(self, info):
        frame_num, timepoint = info

        fig, axs = plt.subplots(1,self.n,figsize=(self.n*8, 8), facecolor='white')
        #fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)
        fig.tight_layout()

        for i,(simulation,plotter, sim_id) in enumerate(zip(self.simulations, self.tp_grid, self.sim_ids)):
            simulation_timepoint = simulation.read_timepoint(timepoint)
            if simulation_timepoint is not None:
                plotter.plot(fig, axs[i], simulation_timepoint, frame_num, timepoint)
        for ax in axs:
            ax.margins(0.01)

        if self.postprocess_grid is not None:
            self.postprocess_grid(fig, axs)

        fig.savefig(os.path.join(self.output_folder_grid, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)

    def visualise(self, name='grid', start=0, stop=None, step=1,
                  postprocess=None, clean_dir=True, cmap=False, auto_execute=True, disable_tqdm=False):
        self.output_folder_grid = os.path.join(self.output_folder, name)
        if os.path.exists(self.output_folder_grid) and clean_dir:
            shutil.rmtree(self.output_folder_grid)
        if not os.path.exists(self.output_folder_grid):
            pathlib.Path(self.output_folder_grid).mkdir(exist_ok=True)

        self.postprocess_grid = postprocess

        self.tp_grid = [
            TimepointPlotterV2()#(marker='o', edgecolors='black', linewidths=0.2, s=40)
            for i in self.simulations]
        for tp in self.tp_grid:
            tp.cmap=cmap

        if auto_execute:
            self.simulations[0].for_timepoint(self.visualise_frame, start=start, stop=stop, step=step, disable_tqdm=disable_tqdm)
        
