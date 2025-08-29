
from ..simulation import Simulation
from ..plotters import TimepointPlotter
import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging
import multiprocessing
import tqdm
from ..config import Config
import re
import errno
import subprocess
import itertools


class RowVisualiser:
    def __init__(self, simulations, output_parent_folder = None, make_folder_if_not_exists=False):
        self.simulations = simulations

        self.sim_ids = [s.iteration for s in simulations]
        self.sim_name = self.simulations[0].name

        self.n = len(simulations)

        self.output_folder:pathlib.Path = Config.output_folder if output_parent_folder is None else pathlib.Path(output_parent_folder)
        if make_folder_if_not_exists: pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        if (not os.path.exists(self.output_folder)): raise FileNotFoundError(self.output_folder)

        self.postprocess_grid = None

        self.plotter = TimepointPlotter
        self.plotter_config = TimepointPlotter.Config()

    def post_frame(self, name:str, frame_num:int, timestep:int, fig:plt.Figure, ax:plt.Axes|np.ndarray[plt.Axes]):
        fig.savefig(self.output_folder.joinpath(name, f'frame_{frame_num}.png'), bbox_inches='tight', pad_inches=None)

    def visualise_frame(self, frame_num:int, timepoint:int)->tuple[plt.Figure,np.ndarray[plt.Axes]]:
        fig, axs = plt.subplots(1,self.n,figsize=(self.n*8, 8), facecolor='white')
        #fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.1, hspace=0.1)
        fig.tight_layout()

        for i,(simulation, sim_id) in enumerate(zip(self.simulations, self.sim_ids)):
            simulation_timepoint = simulation.read_timepoint(timepoint)
            if simulation_timepoint is not None:
                self.plotter.plot(fig, axs[i], simulation_timepoint, frame_num, simulation_timepoint.timestep, sim=simulation, config=self.plotter_config)
        for ax in axs:
            ax.margins(0.01)

        if self.postprocess_grid is not None:
            self.postprocess_grid(fig, axs)
        return fig, axs
    
    def _visualise_frame(self, info:tuple[int,int, str]):
        try:
            frame_num, timestep, name = info
            fig, ax = self.visualise_frame(frame_num, timestep)
            if fig is not None:
                self.post_frame(name, frame_num, timestep, fig, ax)
                plt.close(fig)
        except Exception as e:
            logging.error(f'Error processing frame #{frame_num}: {e}')
            raise e

    def visualise(self, name='grid', start=0, stop=60000, step=6000, maxproc=8,
                  postprocess=None, clean_dir=True, disable_tqdm=False):
        self.create_output_folder(name, clean_dir=clean_dir)
        self.postprocess_grid = postprocess

        times = list(range(start, stop, step))
        with multiprocessing.Pool(processes=maxproc, maxtasksperchild=8) as p:
            _ = list(tqdm.tqdm(p.imap(
                self._visualise_frame, zip(range(len(times)), times, itertools.repeat(name))),
                total=len(times), disable=disable_tqdm))
        
        
    def create_output_folder(self, name='grid', *, clean_dir:bool=False):
        output_folder = self.output_folder.joinpath(name)
        if os.path.exists(output_folder) and clean_dir:
            shutil.rmtree(output_folder)
        if not os.path.exists(output_folder):
            pathlib.Path(output_folder).mkdir(exist_ok=True)

    def cleanup_output_folder(self, name='grid'):
        output_folder = self.output_folder.joinpath(name)
        if output_folder.exists(): shutil.rmtree(output_folder)
        p = self.output_folder.joinpath(f'{name}.ffcat')
        if p.exists(): os.remove(p)

    def create_ffcat(self, name='grid', *, framerate=30):
        output_folder = self.output_folder.joinpath(name)
        if not output_folder.exists(): return

        files = []
        r = re.compile(r"frame_\d+\..*")
        for f in output_folder.glob("frame_*"):
            if r.match(f.name):
                files.append((int(f.name.lstrip('frame_').split('.')[0]), f))
        files.sort()
        
        with open(self.output_folder.joinpath(f'{name}.ffcat'), 'w') as f:
            f.writelines([f"file {p[1]}\r\nduration {1.0/framerate}\r\n" for p in files])

    def generate_mp4_from_ffcat(self, name='grid', *, framerate:int=30):
        cat_file:pathlib.Path = self.output_folder.joinpath(f'{name}.ffcat').resolve()
        if not cat_file.exists(): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), cat_file)
        out_file:pathlib.Path = self.output_folder.joinpath(f'{name}.mp4').resolve()
        print(str(cat_file))
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
        