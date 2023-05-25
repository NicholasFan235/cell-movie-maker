
from .simulation import Simulation
from .simulation_visualiser import AbstractSimulationVisualiser
from .timepoint_plotter import TimepointPlotter, HistogramPlotter, TumourTimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2, TumourTimepointPlotterV2, OxygenTimepointPlotterV2, PressureTimepointPlotterV2
from .strip_distribution_plotter import StripPressureDistributionPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMPressureVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.figsize=(4,12)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("A;B;C", figsize=self.figsize)
        #ax.margins(0.01)
        self.tp.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)

        self.pressure_tp.plot(fig, axs['B'], simulation_timepoint, frame_num, timepoint)
        axs['B'].set_title('Pressure')
        axs['B'].set_yticks([])
        axs['B'].set_xticks([])

        self.oxygen_tp.plot(fig, axs['C'], simulation_timepoint, frame_num, timepoint)
        axs['C'].set_title('Oxygen')
        axs['C'].set_yticks([])
        axs['C'].set_xticks([])


        if self.postprocess is not None:
            self.postprocess(fig, axs)

        fig.tight_layout()
        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, auto_execute=True, maxproc=64, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True
        self.tp = TimepointPlotterV2()
        self.oxygen_tp = OxygenTimepointPlotterV2()
        self.pressure_tp = PressureTimepointPlotterV2()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc)

class TCellABMPressureVisualiser2(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.figsize=(4,12)

    def visualise_frame(self, info):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("A;B;C", figsize=self.figsize)
        #ax.margins(0.01)
        self.tp.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)

        self.pressure_tp.plot(fig, axs['B'], simulation_timepoint, frame_num, timepoint)
        axs['B'].set_title('Pressure')

        self.distribution_tp.plot(fig, axs['C'], simulation_timepoint, frame_num, timepoint)
        axs['C'].set_title('Pressure along x-axis')


        if self.postprocess is not None:
            self.postprocess(fig, axs)

        fig.tight_layout()
        fig.savefig(os.path.join(self.output_folder, 'frame_{}.png'.format(frame_num)))
        plt.close(fig)
        return

    def visualise(self, auto_execute=True, maxproc=64, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True
        self.tp = TimepointPlotterV2()
        self.distribution_tp = StripPressureDistributionPlotter()
        self.pressure_tp = PressureTimepointPlotterV2()

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc)

