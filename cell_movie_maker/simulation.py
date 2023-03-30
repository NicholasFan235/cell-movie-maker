
from .simulation_timepoint import SimulationTimepoint
import os
import re
import multiprocessing
import tqdm
import pathlib


class Simulation:
    def __init__(self, results_folder:str, sampling_timestep_multiple:int=60, timesteps_per_hour:int=120):
        self.results_folder = pathlib.Path(results_folder)
        assert self.results_folder.is_dir(), f'{self.results_folder} does not exist, or is a file.'

        self.id = os.path.basename(os.path.dirname(results_folder))
        self.name = os.path.basename(os.path.dirname(os.path.dirname(results_folder)))

        self.sampling_timestep_multiple = sampling_timestep_multiple
        self.timesteps_per_hour = timesteps_per_hour
        
        self.get_filenames()
        
    def get_filenames(self):
        self.all_files = os.listdir(self.results_folder)

        p = re.compile('^results_(\d+)\.vtu$')
        self.results_timesteps = sorted(list(
            map(lambda x: int(p.match(x)[1]), filter(p.match, self.all_files))))
    
    def read_timepoint(self, timestep:int):
        if timestep > max(self.results_timesteps):
            return SimulationTimepoint(self.id, self.name, self.results_folder, max(self.results_timesteps))
        if timestep not in self.results_timesteps: return None
        return SimulationTimepoint(self.id, self.name, self.results_folder, timestep)

    def for_timepoint(self, func, start=0, stop=None, step=1):
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, 32)) as pool:
            _=list(tqdm.tqdm(pool.imap(func,
                enumerate(self.results_timesteps[start:stop:step], start=start)),
                total=len(self.results_timesteps[start:stop:step])))
    
    def for_final_timepoint(self, func):
        func((len(self.results_timesteps)-1, self.results_timesteps[-1]))

