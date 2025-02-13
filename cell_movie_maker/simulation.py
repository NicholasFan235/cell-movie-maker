
from .simulation_timepoint import SimulationTimepoint, MacrophageSimulationTimepoint, LiverMetSimulationTimepoint
import os
import re
import multiprocessing
import tqdm
import pathlib
import json
from .config import Config
import errno
import typing
import itertools

sim_iteration_regex = re.compile(r'sim_(?P<iteration>\d+)')

class Simulation:
    class Timepoints:
        def __init__(self, simulation):
            self.sim = simulation

        def __getitem__(self, index:int):
            match index:
                case int():
                    return self.sim.read_timepoint(self.sim.results_timesteps[index])
                case slice():
                    return [self.sim.read_timepoint(tp) for tp in self.sim.results_timesteps[index]]
                case _:
                    raise IndexError

    def __init__(self, results_folder:str|pathlib.Path, sampling_timestep_multiple:int=60, timesteps_per_hour:int=120):
        self.results_folder:pathlib.Path = pathlib.Path(results_folder)
        if not self.results_folder.name == 'results_from_time_0': self.results_folder = self.results_folder.joinpath('results_from_time_0')
        assert self.results_folder.is_dir(), f'{self.results_folder} does not exist, or is a file.'

        self.id:str = self.results_folder.parent.name # e.g. sim_0
        self.name:str = self.results_folder.parent.parent.name # experiment name
        m = sim_iteration_regex.match(self.id)
        if m: self.iteration = int(m['iteration'])

        self.sampling_timestep_multiple = sampling_timestep_multiple
        self.timesteps_per_hour = timesteps_per_hour
        
        self.get_filenames()
        self.read_parameters()
        self.timepoints = Simulation.Timepoints(self)
        
    def get_filenames(self):
        self.all_files = os.listdir(self.results_folder)

        p = re.compile(r'^results_(\d+)\.vtu$')
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

    def for_timepoint(self, func, start=0, stop=None, step=1, maxproc=64, disable_tqdm=False):
        N = len(self.results_timesteps[slice(start, stop, step)])
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
            _=list(tqdm.tqdm(pool.imap(func, zip(itertools.repeat(self), self.timepoints[start:stop:step], range(N))),
                total=N, disable=disable_tqdm))
    
    def for_timepoint_single_thread(self, func, start=0, stop=None, step=1, disable_tqdm=False):
        N = len(self.results_timesteps[start:step:step])
        _ = [func((self,tp, i)) for i, tp in tqdm.tqdm(enumerate(self.timepoints[start:stop:step]), total=N, disable=disable_tqdm)]

    def for_final_timepoint(self, func):
        func(self, self.timepoints[-1], 0)


class MacrophageSimulation(Simulation):
    def read_timepoint(self, timestep:int):
        if timestep > max(self.results_timesteps):
            return MacrophageSimulationTimepoint(self.id, self.name, self.results_folder, max(self.results_timesteps))
        if timestep not in self.results_timesteps: return None
        return MacrophageSimulationTimepoint(self.id, self.name, self.results_folder, timestep)

class LiverMetSimulation(Simulation):
    def read_timepoint(self, timestep:int):
        if timestep > max(self.results_timesteps):
            return LiverMetSimulationTimepoint(self.id, self.name, self.results_folder, max(self.results_timesteps))
        if timestep not in self.results_timesteps: return None
        return LiverMetSimulationTimepoint(self.id, self.name, self.results_folder, timestep)
    
    def read_parameters(self):
        pass


def load_simulation(experiment:str, id:int|str=None, cls:typing.Type[Simulation]=Simulation):
    if isinstance(id, int): id = f'sim_{id}'
    
    assert issubclass(cls, Simulation)
    match experiment,id:
        case str(), str():
            try:
                glob = f'**/{experiment}/{id}/results_from_time_0'
                results_folder = next(Config.simulations_folder.glob(glob))
                return cls(results_folder)
            except StopIteration:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pathlib.Path(Config.simulations_folder, glob))
        case int(), None:
            try:
                glob = f'**/sim_{experiment}/results_from_time_0'
                results_folder = next(Config.simulations_folder.glob(glob))
                return cls(results_folder)
            except StopIteration:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pathlib.Path(Config.simulations_folder, glob))
        case str(), None:
            try:
                glob = f'**/{experiment}/results_from_time_0'
                results_folder = next(Config.simulations_folder.glob(glob))
                return cls(results_folder)
            except StopIteration:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pathlib.Path(Config.simulations_folder, glob))
        case _:
            raise RuntimeError("Bad arguments")
    