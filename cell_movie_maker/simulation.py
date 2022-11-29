
from .simulation_timepoint import SimulationTimepoint
import os
import re
import multiprocessing


class Simulation:
    def __init__(self, results_folder:str, sampling_timestep_multiple:int=60, timesteps_per_hour:int=120):
        self.results_folder = results_folder
        self.sampling_timestep_multiple = sampling_timestep_multiple
        self.timesteps_per_hour = timesteps_per_hour
        
        self.get_filenames()
        
    def get_filenames(self):
        self.all_files = os.listdir(self.results_folder)

        p = re.compile('^results_(\d+)\.vtu$')
        self.results_timesteps = sorted(list(
            map(lambda x: int(p.match(x)[1]), filter(p.match, self.all_files))))
    
    def read_timepoint(self, timestep:int):
        results_file = 'results_{}.vtu'.format(timestep)
        return SimulationTimepoint(os.path.join(self.results_folder, results_file))

    def for_timepoint(self, func, step=1):
        with multiprocessing.Pool() as pool:
            pool.map(func, enumerate(self.results_timesteps[::step]))
    
    def for_final_timepoint(self, func):
        func((len(self.results_timesteps)-1, self.results_timesteps[-1]))

