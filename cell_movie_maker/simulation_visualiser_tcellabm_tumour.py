
from .simulation import Simulation
from .simulation_visualiser import AbstractSimulationVisualiser
from .timepoint_plotter import TimepointPlotter, HistogramPlotter, TumourTimepointPlotter
from .timepoint_plotter_v2 import TimepointPlotterV2, TumourTimepointPlotterV2, OxygenTimepointPlotterV2, PressureTimepointPlotterV2
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMTumourVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.figsize=(12,8)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("AAB;AAC", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotterV2.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)

        PressureTimepointPlotterV2.plot(fig, axs['B'], simulation_timepoint, frame_num, timepoint)
        axs['B'].set_title('Pressure')
        axs['B'].set_yticks([])
        axs['B'].set_xticks([])

        OxygenTimepointPlotterV2.plot(fig, axs['C'], simulation_timepoint, frame_num, timepoint)
        axs['C'].set_title('Oxygen')
        axs['C'].set_yticks([])
        axs['C'].set_xticks([])

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

class TCellABMTumourVisualiserV2(AbstractSimulationVisualiser):
    def __init__(self, simulation:Simulation, visualisation_name='standard', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)
        self.figsize=(16,8)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        fig, axs = plt.subplot_mosaic("AABC;AADE", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotterV2.plot(fig, axs['A'], simulation_timepoint, frame_num, timepoint)

        axs['B'].set_title('Oxygen')
        axs['B'].set_yticks([])
        axs['B'].set_xticks([])
        ox = axs['B'].imshow(simulation_timepoint.oxygen_data, cmap='cividis', vmin=0, vmax=1, origin='lower')
        fig.colorbar(ox, ax=axs['B'])

        PressureTimepointPlotterV2.plot(fig, axs['C'], simulation_timepoint, frame_num, timepoint)
        axs['C'].set_title('Pressure')
        axs['C'].set_yticks([])
        axs['C'].set_xticks([])

        axs['D'].set_title('CCL5 (Chemoattractant)')
        axs['D'].set_yticks([])
        axs['D'].set_xticks([])
        ccl5data = simulation_timepoint.ccl5_data
        ccl5 = axs['D'].imshow(ccl5data, cmap='magma', vmin=0, vmax=100, origin='lower')
        fig.colorbar(ccl5, ax=axs['D'])

        axs['E'].set_title('ECM Density')
        axs['E'].set_yticks([])
        axs['E'].set_xticks([])
        ecm_density_data = simulation_timepoint.ecm_density_data
        density = axs['E'].imshow(ecm_density_data, cmap='binary', vmin=0, vmax=1, origin='lower')
        fig.colorbar(density, ax=axs['E'])

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


