
from .simulation import Simulation
from .simulation_timepoint import SimulationTimepoint
from .plotters import TimepointPlotter, TumourTimepointPlotter, PressureTimepointPlotter, MacrophageTimepointPlotter, TumourDamageHistogramPlotter, TCellExhaustionHistogramPlotter, ChemokinePDETimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging
import re
import subprocess
import errno
from.config import Config


class AbstractSimulationVisualiser:
    def __init__(self, visualisation_name = 'abstract', output_parent_folder = None, make_folder_if_not_exists=False):
        self.visualisation_name = visualisation_name
        self.figsize = (8,8)
        self.postprocess = None

        self.label_frames_with_timestep=True
        
        self.output_folder:pathlib.Path = Config.output_folder if output_parent_folder is None else pathlib.Path(output_parent_folder)
        if make_folder_if_not_exists: pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        if (not os.path.exists(self.output_folder)): raise FileNotFoundError(self.output_folder)

        
    def post_frame(self, sim:Simulation, timepoint:SimulationTimepoint, frame_num:int, fig:plt.Figure, ax:plt.Axes|np.ndarray[plt.Axes]):
        fig.savefig(self.output_folder.joinpath(sim.name, sim.id, self.visualisation_name, 'frame_{}.png'.format(timepoint.timestep if self.label_frames_with_timestep else frame_num)))

    def visualise_frame(self, sim:Simulation, timepoint:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        raise NotImplementedError()
    
    def _visualise_frame(self, args:tuple[Simulation,SimulationTimepoint,int]):
        try:
            fig, ax = self.visualise_frame(*args)
            if fig is not None:
                if self.postprocess is not None:
                    self.postprocess(fig, ax, *args)
                self.post_frame(*args, fig, ax)
                plt.close(fig)
        except Exception as e:
            logging.error(f'Error processing frame #{args[1]}: {e}')
            raise e

    def visualise(self, sim, start=0, stop=None, step=1, clean_dir=True, maxproc=64, auto_execute=True, disable_tqdm=False):
        self.create_output_folder(sim, clean_dir=clean_dir)

        sim.for_timepoint(self._visualise_frame, start=start, stop=stop, step=step, maxproc=maxproc, disable_tqdm=disable_tqdm)
    
    def create_output_folder(self, sim, *, clean_dir:bool):
        output_folder:pathlib.Path = self.output_folder.joinpath(sim.name, sim.id, self.visualisation_name)
        if os.path.exists(output_folder) and clean_dir:
            shutil.rmtree(output_folder)
        if not os.path.exists(output_folder):
            pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    def cleanup_output_folder(self, sim):
        output_folder:pathlib.Path = self.output_folder.joinpath(sim.name, sim.id, self.visualisation_name)
        if output_folder.exists(): shutil.rmtree(output_folder)
        p = self.output_folder.joinpath(sim.name, sim.id, f'{self.visualisation_name}.ffcat')
        if p.exists(): os.remove(p)

    def create_ffcat(self, sim, *, framerate=30):
        output_folder:pathlib.Path = self.output_folder.joinpath(sim.name, sim.id, self.visualisation_name)
        if not output_folder.exists(): return

        files = []
        r = re.compile(r"frame_\d+\..*")
        for f in output_folder.glob("frame_*"):
            if r.match(f.name):
                files.append((int(f.name.lstrip('frame_').split('.')[0]), f))
        files.sort()
        
        with open(self.output_folder.joinpath(sim.name, sim.id, f'{self.visualisation_name}.ffcat'), 'w') as f:
            f.writelines([f"file {p[1]}\r\nduration {1.0/framerate}\r\n" for p in files])

    def generate_mp4_from_ffcat(self, sim, *, framerate:int=30):
        cat_file:pathlib.Path = self.output_folder.joinpath(sim.name, sim.id, f'{self.visualisation_name}.ffcat')
        if not cat_file.exists(): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), cat_file)
        out_file:pathlib.Path = self.output_folder.joinpath(sim.name, sim.id, f'{self.visualisation_name}.mp4')
        
        subprocess.call([
            'ffmpeg',
            '-y',
            '-safe', '0',
            '-f', 'concat',
            '-i', str(cat_file),
            #'-framerate', str(framerate),
            '-c:v', 'libx264',
            '-r', str(framerate),
            '-pix_fmt', 'yuv420p',
            #'-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
            '-vf', 'scale=-1:-1,pad=ceil(iw/2)*2:ceil(ih/2)*2',
            '-loglevel', 'error',
            '-hide_banner',
            str(out_file)
        ])
        
    def generate_mp4(self, sim, *, framerate:int=30):
        in_files = self.output_folder.joinpath(sim.name, sim.id, self.visualisation_name, 'frame_*.png')
        out_file = self.output_folder.joinpath(sim.name, sim.id, f'{self.visualisation_name}.mp4')
        subprocess.call([
            'ffmpeg',
            "-y",
            "-framerate", str(framerate),
            #"-pattern_type", "glob"
            "-i", str(in_files),
            "-start_number", str(0),
            "-c:v", "libx264",
            "-r", str(framerate),
            "-pix_fmt", "yuv420p",
            '-loglevel', 'error',
            '-hide_banner',
            str(out_file)
        ])

class SimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.plotter_config = TimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes]:
        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        TimepointPlotter.plot(fig, ax, tp, frame_num, tp.timestep, sim=sim, config=self.plotter_config)
        return fig, ax


class TumourSimulationVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard_tumour', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.tumour_plotter_config = TumourTimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes]:
        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        TumourTimepointPlotter.plot(fig, ax, tp, frame_num, tp.timestep, sim=sim, config=self.tumour_plotter_config)
        return fig, ax


class HistogramVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='histogram', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.tumour_damage_histogram_plotter_config = TumourDamageHistogramPlotter.Config()
        self.tcell_exhaustion_histogram_plotter_config = TCellExhaustionHistogramPlotter.Config()
        self.plotter_config = TimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplot_mosaic("AB;AC", figsize=self.figsize)
        TimepointPlotter.plot(fig, axs['A'], tp, frame_num, tp.timestep, config=self.plotter_config)
        TCellExhaustionHistogramPlotter.plot(fig, axs['B'], tp, sim=sim, config=self.tcell_exhaustion_histogram_plotter_config)
        TumourDamageHistogramPlotter.plot(fig, axs['C'], tp, sim=sim, config=self.tumour_damage_histogram_plotter_config)
        return fig, axs


class ChemokineVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name, chemokine_name=None, **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.chemokine_name = self.visualisation_name if chemokine_name is None else chemokine_name
        self.chemokine_pde_plotter_config = ChemokinePDETimepointPlotter.Config(
            chemokine=self.chemokine_name, cmap='jet', imshow_kwargs=dict())

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes]:
        data = tp.read_pde(self.chemokine_name)
        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        fig.tight_layout()
        ChemokinePDETimepointPlotter.plot(fig, ax, tp, frame_num, tp.timestep, sim=sim, config=self.chemokine_pde_plotter_config)
        return fig, ax


class PressureVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='pressure', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.pressure_plotter_config = PressureTimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes]:
        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        PressureTimepointPlotter.plot(fig, ax, tp, frame_num, tp.timestep, sim=sim, config=self.pressure_plotter_config)
        return fig, ax
    

class MacrophageVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='standard_macrophages', **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.macrophage_plotter_config = MacrophageTimepointPlotter.Config()

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int)->tuple[plt.Figure,plt.Axes]:
        fig, ax = plt.subplots(1,1, figsize=self.figsize)
        #ax.margins(0.01)
        fig.tight_layout()
        MacrophageTimepointPlotter.plot(fig, ax, tp, frame_num, tp.timestep, sim=sim, config=self.macrophage_plotter_config)
        return fig, ax

