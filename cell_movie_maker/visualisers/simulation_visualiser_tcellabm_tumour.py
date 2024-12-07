
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ..simulation_visualiser import AbstractSimulationVisualiser
from ..plotters import TimepointPlotter, TumourTimepointPlotter, OxygenTimepointPlotter, PressureTimepointPlotter, ChemokinePDETimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMTumourVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.figsize=(12,8)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.oxygen_plotter_config = OxygenTimepointPlotter.Config()
        self.pressure_plotter_config = PressureTimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AAB;AAC", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)

        PressureTimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.pressure_plotter_config)
        axs['B'].set_title('Pressure')

        OxygenTimepointPlotter.plot(fig, axs['C'], tp, frame_num, tp.timestep, sim=sim, config=self.oxygen_plotter_config)
        axs['C'].set_title('Oxygen')

        fig.tight_layout()
        return fig, axs


class TCellABMTumourVisualiserV2(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.figsize=(16,8)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.oxygen_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='oxygen', cmap='cividis', vmin=0, vmax=1, imshow_kwargs=dict(origin='lower'))
        self.pressure_plotter_config = PressureTimepointPlotter.Config()
        self.ccl5_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='ccl5', cmap='magma', vmin=0, vmax=100, imshow_kwargs=dict(origin='lower'))
        self.ecm_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='density', cmap='binary', vmin=0, vmax=1, imshow_kwargs=dict(origin='lower'))

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AABC;AADE", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)

        axs['B'].set_title('Oxygen')
        ChemokinePDETimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.oxygen_pde_plotter_config)

        PressureTimepointPlotter.plot(fig, axs['C'], tp, frame_num, tp.timestep, sim=sim, config=self.pressure_plotter_config)
        axs['C'].set_title('Pressure')
        axs['C'].set_yticks([])
        axs['C'].set_xticks([])

        axs['D'].set_title('CCL5 (Chemoattractant)')
        axs['D'].set_yticks([])
        axs['D'].set_xticks([])
        ChemokinePDETimepointPlotter.plot(fig, axs['D'], tp, frame_num, tp.timestep, sim=sim, config=self.ccl5_pde_plotter_config)

        axs['E'].set_title('ECM Density')
        axs['E'].set_yticks([])
        axs['E'].set_xticks([])
        ChemokinePDETimepointPlotter.plot(fig, axs['E'], tp, frame_num, tp.timestep, sim=sim, config=self.ecm_pde_plotter_config)

        fig.tight_layout()
        return fig, axs

