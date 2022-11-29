
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np

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
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        ax.margins(0.01)
        self.tp.plot(ax, simulation_timepoint, self.sim_name, self.sim_id, frame_num, timepoint)

        if self.postprocess_standard is not None:
            self.postprocess_standard(ax)

        fig.savefig(os.path.join(self.output_folder_standard, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)

    def visualise(self, start=0, stop=None, step=1,
                  postprocess=None, clean_dir=True, cmap=False):
        self.output_folder_standard = os.path.join(self.output_folder, 'standard')
        if os.path.exists(self.output_folder_standard) and clean_dir:
            shutil.rmtree(self.output_folder_standard)
        if not os.path.exists(self.output_folder_standard):
            os.mkdir(self.output_folder_standard)

        self.postprocess_standard = postprocess

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.tp.cmap=cmap
        self.sim.for_timepoint(self.visualise_frame, start=start, stop=stop, step=step)

    def visualise_histogram_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("AB;AC", figsize=(16,8))
        self.tp.plot(axs['A'], simulation_timepoint, self.sim_name, self.sim_id, frame_num, timepoint)
        self.tp.cytotoxic_histogram(axs['B'], simulation_timepoint)
        self.tp.tumour_histogram(axs['C'], simulation_timepoint)

        if self.postprocess_histogram is not None:
            self.postprocess_histogram(axs)

        fig.savefig(os.path.join(self.output_folder_histogram, 'frame_histogram_{}.png'.format(frame_num)))
        plt.close(fig)


    def visualise_histogram(self, start=0, stop=None, step=1,
                            postprocess=None, clean_dir=True, cmap=False):
        self.output_folder_histogram = os.path.join(self.output_folder, 'histogram')
        if os.path.exists(self.output_folder_histogram) and clean_dir:
            shutil.rmtree(self.output_folder_histogram)
        if not os.path.exists(self.output_folder_histogram):
            os.mkdir(self.output_folder_histogram)

        self.postprocess_histogram = postprocess

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.tp.cmap = cmap
        self.sim.for_timepoint(self.visualise_histogram_frame, start=start, stop=stop, step=step)
        #self.sim.for_final_timepoint(self.visualise_histogram_frame)
        
