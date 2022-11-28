
from .simulation import Simulation
from .timepoint_plotter import TimepointPlotter
import matplotlib.pylab as plt
import os
import shutil

class SimulationVisualiser:
    def __init__(self, simulation_folder):
        results_folder = os.path.join(simulation_folder, 'results_from_time_0')
        self.sim_id = os.path.basename(os.path.dirname(results_folder))
        self.sim = Simulation(results_folder)
        if (not os.path.exists('visualisations')):
            os.mkdir('visualisations')
        self.output_folder = os.path.join('visualisations', self.sim_id)

    def visualise_frame(self, info):
        id, frame = info
        simulation_timepoint = self.sim.read_timepoint(frame)

        fig, ax = plt.subplots(1,1, figsize=(8,8))
        ax.axis('off')
        ax.margins(0.01)
        self.tp.plot(ax, simulation_timepoint)
        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(id)))
        plt.close(fig)

    def visualise(self, step=1):
        if (os.path.exists(self.output_folder)):
            shutil.rmtree(self.output_folder)
        os.mkdir(self.output_folder)

        self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        self.sim.for_timepoint(self.visualise_frame, step=step)

