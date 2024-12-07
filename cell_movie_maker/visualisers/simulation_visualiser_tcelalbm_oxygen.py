
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ..simulation_visualiser import AbstractSimulationVisualiser
from ..plotters import TimepointPlotter, OxygenTimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMOxygenVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.oxygen_plotter_config = OxygenTimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("A;B", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)
        OxygenTimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.oxygen_plotter_config)
        axs['B'].set_title('Oxygen')
        fig.tight_layout()
        return fig, axs

