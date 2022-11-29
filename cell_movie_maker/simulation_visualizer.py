
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np

import warnings
warnings.filterwarnings("ignore")

class SimulationVisualiser:
    def __init__(self, simulation_folder):
        results_folder = os.path.join(simulation_folder, 'results_from_time_0')
        self.sim_id = os.path.basename(os.path.dirname(results_folder))
        self.sim_name = os.path.basename(os.path.dirname(os.path.dirname(results_folder)))
        self.sim = Simulation(results_folder)
        if (not os.path.exists('visualisations')):
            os.mkdir('visualisations')
        if (not os.path.exists(os.path.join('visualisations', self.sim_name))):
            os.mkdir(os.path.join('visualisations', self.sim_name))
        self.output_folder = os.path.join('visualisations', self.sim_name, self.sim_id)
        if not os.path.exists(self.output_folder):
            os.mkdir(self.output_folder)

    def visualise_frame(self, info):
        id, frame = info
        simulation_timepoint = self.sim.read_timepoint(frame)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f'{self.sim_name}/{self.sim_id} #{id} t={frame/60/24:.1f}d')
        ax.margins(0.01)
        self.tp.plot(ax, simulation_timepoint)
        fig.savefig(os.path.join(self.output_folder_standard, 'frame_{}.png'.format(id)))
        plt.close(fig)

    def visualise(self, step=1):
        self.output_folder_standard = os.path.join(self.output_folder, 'standard')
        if (os.path.exists(self.output_folder_standard)):
            shutil.rmtree(self.output_folder_standard)
        os.mkdir(self.output_folder_standard)

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.sim.for_timepoint(self.visualise_frame, step=step)

    def visualise_histogram_frame(self, info):
        id, frame = info
        simulation_timepoint = self.sim.read_timepoint(frame)

        fig, axs = plt.subplot_mosaic("AB;AC", figsize=(16,8))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].margins(0.01)
        axs['A'].set_title(f'{self.sim_name}/{self.sim_id} #{id} t={frame/60/24:.1f}d')
        self.tp.plot(axs['A'], simulation_timepoint)
        self.tp.cytotoxic_histogram(axs['B'], simulation_timepoint)
        self.tp.tumour_histogram(axs['C'], simulation_timepoint)

        fig.savefig(os.path.join(self.output_folder_histogram, 'frame_histogram_{}.png'.format(id)))
        plt.close(fig)


    def visualise_histogram(self, step=1):
        self.output_folder_histogram = os.path.join(self.output_folder, 'histogram')
        if (os.path.exists(self.output_folder_histogram)):
            shutil.rmtree(self.output_folder_histogram)
        os.mkdir(self.output_folder_histogram)

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.sim.for_timepoint(self.visualise_histogram_frame, step=step)
        #self.sim.for_final_timepoint(self.visualise_histogram_frame)
        
