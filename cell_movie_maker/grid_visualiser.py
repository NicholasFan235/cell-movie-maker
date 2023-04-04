
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np

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
            os.mkdir(output_parent_folder)
        self.output_folder = os.path.join(output_parent_folder, self.sim_name)
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)

    def visualise_frame(self, info):
        frame_num, timepoint = info

        fig, axs = plt.subplots(self.shape[0],self.shape[1],figsize=(self.shape[0]*8,self.shape[1]*8))
        #fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)

        for i,(_simulations,_plotters, _ids) in enumerate(zip(self.simulation_grid, self.tp_grid, self.sim_ids)):
            for j,(simulation,plotter, sim_id) in enumerate(zip(_simulations, _plotters, _ids)):
                simulation_timepoint = simulation.read_timepoint(timepoint)
                plotter.plot(fig, axs[i][j], simulation_timepoint, frame_num, timepoint)

        if self.postprocess_grid is not None:
            self.postprocess_grid(axs)

        fig.savefig(os.path.join(self.output_folder_grid, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)

    def visualise(self, name='grid', start=0, stop=None, step=1,
                  postprocess=None, clean_dir=True, cmap=False, auto_execute=True):
        self.output_folder_grid = os.path.join(self.output_folder, name)
        if os.path.exists(self.output_folder_grid) and clean_dir:
            shutil.rmtree(self.output_folder_grid)
        if not os.path.exists(self.output_folder_grid):
            os.mkdir(self.output_folder_grid)

        self.postprocess_grid = postprocess

        self.tp_grid = [[
            TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=40)
            for i in j] for j in self.simulation_grid]
        for tps in self.tp_grid:
            for tp in tps:
                tp.cmap=cmap

        if auto_execute:
            self.simulation_grid[0][0].for_timepoint(self.visualise_frame, start=start, stop=stop, step=step)
        
