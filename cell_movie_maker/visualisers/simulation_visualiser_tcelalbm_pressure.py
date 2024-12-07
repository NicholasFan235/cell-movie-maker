
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ..simulation_visualiser import AbstractSimulationVisualiser
from ..plotters import TimepointPlotter, OxygenTimepointPlotter, PressureTimepointPlotter
from ..plotters.legacy_plotters.strip_distribution_plotter import StripPressureDistributionPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMPressureVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.oxygen_plotter_config = OxygenTimepointPlotter.Config()
        self.pressure_plotter_config = PressureTimepointPlotter.Config()
        self.figsize=(4,12)

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("A;B;C", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)

        PressureTimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.pressure_plotter_config)
        axs['B'].set_title('Pressure')

        OxygenTimepointPlotter.plot(fig, axs['C'], tp, frame_num, tp.timestep, sim=sim, config=self.oxygen_plotter_config)
        axs['C'].set_title('Oxygen')

        fig.tight_layout()
        return fig, axs


class TCellABMPressureVisualiser2(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.pressure_plotter_config = PressureTimepointPlotter.Config()
        self.figsize=(4,12)

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("A;B;C", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)

        PressureTimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.pressure_plotter_config)
        axs['B'].set_title('Pressure')

        StripPressureDistributionPlotter.plot(fig, axs['C'], tp, frame_num, tp.timestep)
        axs['C'].set_title('Pressure along x-axis')

        fig.tight_layout()
        return fig, axs

