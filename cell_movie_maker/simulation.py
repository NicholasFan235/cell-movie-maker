
from .simulation_timepoint import SimulationTimepoint, MacrophageSimulationTimepoint
import os
import re
import multiprocessing
import tqdm
import pathlib
import json


class Simulation:
    def __init__(self, results_folder:str, sampling_timestep_multiple:int=60, timesteps_per_hour:int=120):
        self.results_folder = pathlib.Path(results_folder) # Path to results_from_time_0
        assert self.results_folder.is_dir(), f'{self.results_folder} does not exist, or is a file.'

        self.id = os.path.basename(os.path.dirname(self.results_folder))
        self.name = os.path.basename(os.path.dirname(os.path.dirname(self.results_folder)))

        self.sampling_timestep_multiple = sampling_timestep_multiple
        self.timesteps_per_hour = timesteps_per_hour
        
        self.get_filenames()
        self.read_parameters()
        
    def get_filenames(self):
        self.all_files = os.listdir(self.results_folder)

        p = re.compile('^results_(\d+)\.vtu$')
        self.results_timesteps = sorted(list(
            map(lambda x: int(p.match(x)[1]), filter(p.match, self.all_files))))
    
    def read_parameters(self):
        self.parameters = None
        params_path = pathlib.Path(self.results_folder.parent, 'params.json')
        if params_path.exists() and params_path.is_file():
            with open(params_path, 'r') as f:
                self.parameters = json.load(f)
    
    def read_timepoint(self, timestep:int):
        if timestep > max(self.results_timesteps):
            return SimulationTimepoint(self.id, self.name, self.results_folder, max(self.results_timesteps))
        if timestep not in self.results_timesteps: return None
        return SimulationTimepoint(self.id, self.name, self.results_folder, timestep)

    def for_timepoint(self, func, start=0, stop=None, step=1, maxproc=64, disable_tqdm=False, offset=0):
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
            _=list(tqdm.tqdm(pool.imap(func,
                enumerate(self.results_timesteps[start:stop:step], start=start+offset)),
                total=len(self.results_timesteps[start:stop:step]), disable=disable_tqdm))
    
    def for_timepoint_single_thread(self, func, start=0, stop=None, step=1, disable_tqdm=False):
        for info in tqdm.tqdm(enumerate(self.results_timesteps[start:stop:step], start=start+offset),
                                     total=len(self.results_timesteps[start:stop:step]), disable=disable_tqdm):
            func(info)

    def for_final_timepoint(self, func):
        func((len(self.results_timesteps)-1, self.results_timesteps[-1]))


class MacrophageSimulation(Simulation):
    def read_timepoint(self, timestep:int):
        if timestep > max(self.results_timesteps):
            return MacrophageSimulationTimepoint(self.id, self.name, self.results_folder, max(self.results_timesteps))
        if timestep not in self.results_timesteps: return None
        return MacrophageSimulationTimepoint(self.id, self.name, self.results_folder, timestep)
    