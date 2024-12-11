import matplotlib.pylab as plt
import os
import shutil
import numpy as np
import pathlib
import logging
import re
import subprocess
import errno
from .experiment import Experiment
from.config import Config


class AbstractExperimentVisualiser:
    def __init__(self, visualisation_name = 'abstract-experiment', output_parent_folder = None, make_folder_if_not_exists=False):
        self.visualisation_name = visualisation_name
        self.figsize = (8,8)
        self.postprocess = None

        self.label_frames_with_timestep=True
        
        self.output_folder:pathlib.Path = Config.output_folder if output_parent_folder is None else pathlib.Path(output_parent_folder)
        if make_folder_if_not_exists: pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        if (not os.path.exists(self.output_folder)): raise FileNotFoundError(self.output_folder)

        
    def post_frame(self, experiment:str, timestep:int, frame_num:int, fig:plt.Figure, ax:plt.Axes|np.ndarray[plt.Axes]):
        fig.savefig(self.output_folder.joinpath(experiment.name, self.visualisation_name, 'frame_{}.png'.format(timestep if self.label_frames_with_timestep else frame_num)))

    def visualise_frame(self, experiment:Experiment, timestep:int, frame_num:int)->tuple[plt.Figure,plt.Axes|np.ndarray[plt.Axes]]:
        raise NotImplementedError()
    
    def _visualise_frame(self, args:tuple[Experiment,int,int]):
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

    def visualise(self, experiment:Experiment, start=0, stop=60000, step=600, clean_dir=True, maxproc=64, auto_execute=True, disable_tqdm=False):
        self.create_output_folder(experiment, clean_dir=clean_dir)

        experiment.for_timepoint(self._visualise_frame, start=start, stop=stop, step=step, maxproc=maxproc, disable_tqdm=disable_tqdm)
    
    def create_output_folder(self, experiment:Experiment, *, clean_dir:bool):
        output_folder:pathlib.Path = self.output_folder.joinpath(experiment.name, self.visualisation_name)
        if os.path.exists(output_folder) and clean_dir:
            shutil.rmtree(output_folder)
        if not os.path.exists(output_folder):
            pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

    def cleanup_output_folder(self, experiment:Experiment):
        output_folder:pathlib.Path = self.output_folder.joinpath(experiment.name, self.visualisation_name)
        if output_folder.exists(): shutil.rmtree(output_folder)
        p = self.output_folder.joinpath(experiment.name, f'{self.visualisation_name}.ffcat')
        if p.exists(): os.remove(p)

    def create_ffcat(self, experiment:Experiment, *, framerate=30):
        output_folder:pathlib.Path = self.output_folder.joinpath(experiment.name, self.visualisation_name)
        if not output_folder.exists(): return

        files = []
        r = re.compile(r"frame_\d+\..*")
        for f in output_folder.glob("frame_*"):
            if r.match(f.name):
                files.append((int(f.name.lstrip('frame_').split('.')[0]), f))
        files.sort()
        
        with open(self.output_folder.joinpath(experiment.name, f'{self.visualisation_name}.ffcat'), 'w') as f:
            f.writelines([f"file {p[1]}\r\nduration {1.0/framerate}\r\n" for p in files])

    def generate_mp4_from_ffcat(self, experiment:Experiment, *, framerate:int=30):
        cat_file:pathlib.Path = self.output_folder.joinpath(experiment.name, f'{self.visualisation_name}.ffcat')
        if not cat_file.exists(): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), cat_file)
        out_file:pathlib.Path = self.output_folder.joinpath(experiment.name, f'{self.visualisation_name}.mp4')
        
        subprocess.call([
            'ffmpeg',
            '-y',
            '-safe', '0',
            '-f', 'concat',
            '-i', f"{str(cat_file)}",
            #'-framerate', str(framerate),
            '-c:v', 'libx264',
            '-r', str(framerate),
            '-pix_fmt', 'yuv420p',
            #'-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
            '-vf', 'scale=-1:-1,pad=ceil(iw/2)*2:ceil(ih/2)*2',
            '-loglevel', 'error',
            '-hide_banner',
            f"{str(out_file)}"
        ])
        
    def generate_mp4(self, experiment:Experiment, *, framerate:int=30):
        in_files = self.output_folder.joinpath(experiment.name, self.visualisation_name, 'frame_*.png')
        out_file = self.output_folder.joinpath(experiment.name, f'{self.visualisation_name}.mp4')
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
            f"{str(out_file)}"
        ])
