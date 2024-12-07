
from ..simulation import Simulation
from ..simulation import SimulationTimepoint
from ..simulation_visualiser import AbstractSimulationVisualiser
from ..plotters import TimepointPlotter, ChemokinePDETimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np


class TCellABMChemokineVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.timepoint_plotter_config = TimepointPlotter.Config()
        self.oxygen_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='oxygen', cmap='cividis', vmin=0, vmax=1, imshow_kwargs=dict(origin='lower'))
        self.ccl5_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='ccl5', cmap='magma', vmin=0, vmax=None, imshow_kwargs=dict(origin='lower'))
        self.ifng_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='ifng', cmap='binary', vmin=0, vmax=1, imshow_kwargs=dict(origin='lower'))
        self.cxcl9_pde_plotter_config = ChemokinePDETimepointPlotter.Config(chemokine='cxcl9', cmap='binary', vmin=0, vmax=1, imshow_kwargs=dict(origin='lower'))
        self.figsize=(16,8)

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AABC;AADE", figsize=self.figsize)
        #ax.margins(0.01)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, sim=sim, config=self.timepoint_plotter_config)

        axs['B'].set_title('Oxygen')
        ChemokinePDETimepointPlotter.plot(fig, axs['B'], tp, frame_num, tp.timestep, sim=sim, config=self.oxygen_pde_plotter_config)

        axs['C'].set_title('CCL5 (Chemoattractant)')
        ChemokinePDETimepointPlotter.plot(fig, axs['C'], tp, frame_num, tp.timestep, sim=sim, config=self.ccl5_pde_plotter_config)

        axs['D'].set_title('IFN-g (Produced by activated T-cells)')
        ChemokinePDETimepointPlotter.plot(fig, axs['D'], tp, frame_num, tp.timestep, sim=sim, config=self.ifng_pde_plotter_config)

        axs['E'].set_title('CXCL-9 (Reduce T-cell motility)')
        ChemokinePDETimepointPlotter.plot(fig, axs['E'], tp, frame_num, tp.timestep, sim=sim, config=self.cxcl9_pde_plotter_config)

        fig.tight_layout()
        return fig, axs

