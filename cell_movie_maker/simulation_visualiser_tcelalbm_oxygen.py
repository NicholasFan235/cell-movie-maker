
from .simulation import Simulation
from .simulation_visualiser import AbstractSimulationVisualiser
from .timepoint_plotter import TimepointPlotter, HistogramPlotter, TumourTimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2, TumourTimepointPlotterV2, OxygenTimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMOxygenVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("A;B", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotterV2.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)

        OxygenTimepointPlotterV2.plot(fig, axs['B'], simulation_timepoint, frame_num, timepoint)
        axs['B'].set_title('Oxygen')
        axs['B'].set_yticks([])
        axs['B'].set_xticks([])


        if self.postprocess is not None:
            self.postprocess(fig, axs)

        fig.tight_layout()
        return fig, axs

    def visualise(self, auto_execute=True, maxproc=64, disable_tqdm=False, *args, **kwargs):
        super().visualise(*args, **kwargs)

        #self.tp = TimepointPlotter(marker='o', edgecolors='black', linewidths=0.2, s=20)
        #self.tp.cmap=True

        if auto_execute:
            self.sim.for_timepoint(self._visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc, disable_tqdm=disable_tqdm)

