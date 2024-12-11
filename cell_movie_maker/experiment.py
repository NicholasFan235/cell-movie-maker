from .simulation import Simulation
import pathlib
import numpy as np
import pandas as pd
import re
import os
import glob
import multiprocessing
import itertools
import tqdm
from .config import Config
import errno
import typing


sim_iteration_regex = re.compile(r'^sim_(?P<iteration>\d+)$')

class Experiment:
    
                
    # class Simulations:
    #     def __init__(self, experiment):
    #         self.experiment = experiment
        
    #     def __getitem__(self, index:int):
    #         match index:
    #             case int():
    #                 return self.experiment.read_simulation(index)
    #             case slice():
    #                 return [self.experiment.read_simulation(p) for p in self.sim_folders[index]]
    #             case _:
    #                 raise IndexError

    def __init__(self, experiment_folder:str|pathlib.Path):
        self.experiment_folder:pathlib.Path = pathlib.Path(experiment_folder)
        assert self.experiment_folder.is_dir(), f'{self.experiment_folder} does not exist, or is a file.'

        self.name:str = self.experiment_folder.name
        self.sim_folders = list(self.experiment_folder.glob("sim_*/results_from_time_0"))

    def read_simulation(self, id:int|str)->Simulation:
        match id:
            case int():
                return Simulation(self.experiment_folder.joinpath(f"sim_{id}/results_from_time_0"))
            case str():
                if sim_iteration_regex.match(id):
                    return Simulation(self.experiment_folder.joinpath(id, "results_from_time_0"))
                else:
                    return Simulation(id)
            case _:
                raise IndexError
    
    def for_timepoint(self, func, start=0, stop=60000, step=600, maxproc=64, disable_tqdm=False):
        N = len(list(range(start,stop,step)))
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
            _=list(tqdm.tqdm(pool.imap(func, zip(itertools.repeat(self), range(start,stop,step), range(N))),
                total=N, disable=disable_tqdm))
    
    def for_timepoint_single_thread(self, func, start=0, stop=60000, step=600, disable_tqdm=False):
        N = len(list(range(start,stop,step)))
        _ = [func((self,tp, i)) for i, tp in tqdm.tqdm(enumerate(range(start,stop,step)), total=N, disable=disable_tqdm)]

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
def load_experiment(name:str, cls:typing.Type[Experiment]=Experiment):
    assert isinstance(name, str)
    
    assert issubclass(cls, Experiment)
    match name:
        case str():
            if Config.simulations_folder.name == name:
                return Experiment(Config.simulations_folder)
            if Config.simulations_folder.joinpath(name).exists():
                return Experiment(Config.simulations_folder.joinpath(name))
            try:
                glob = f'**/{name}'
                results_folder = next(Config.simulations_folder.glob(glob))
                return cls(results_folder)
            except StopIteration:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), pathlib.Path(Config.simulations_folder, glob))
        case _:
            raise RuntimeError("Bad arguments")
    