from __future__ import annotations

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
sim_iteration_regex_search = re.compile(r'/sim_(?P<iteration>\d+)/')

class Experiment:
    
                
    class Simulations:
        def __init__(self, experiment):
            self.experiment = experiment
        
        def __getitem__(self, index:int):
            s = Simulation if Config.simulation_class is None else Config.simulation_class
            # print("Simulation Class: ", s)
            match index:
                case int():
                    return s(self.experiment.sim_folders[index])
                case slice():
                    return [s(p) for p in self.experiment.sim_folders[index]]
                case _:
                    raise IndexError
        
        def __len__(self):
            return len(self.experiment.sim_ids)

    def __init__(self, experiment_folder:str|pathlib.Path):
        self.experiment_folder:pathlib.Path = pathlib.Path(experiment_folder)
        assert self.experiment_folder.is_dir(), f'{self.experiment_folder} does not exist, or is a file.'

        self.name:str = self.experiment_folder.name

        sim_folders = sorted([(int(sim_iteration_regex_search.search(str(f))["iteration"]), f) for f in self.experiment_folder.glob("sim_*/results_from_time_0")])
        self.sim_folders:list[str] = [f[1] for f in sim_folders]
        self.sim_ids:list[int] = [f[0] for f in sim_folders]
        self.simulations = Experiment.Simulations(self)

    def read_simulation(self, id:int|str)->Simulation:
        s = Simulation if Config.simulation_class is None else Config.simulation_class
        # print("Simulation Class:", s)
        match id:
            case int():
                return s(self.experiment_folder.joinpath(f"sim_{id}/results_from_time_0"))
            case str():
                if sim_iteration_regex.match(id):
                    return s(self.experiment_folder.joinpath(id, "results_from_time_0"))
                else:
                    return s(id)
            case _:
                raise IndexError
    
    def for_timepoint(self, func:typing.Callable[[Experiment,int,int],None], start=0, stop=60000, step=600, maxproc=64, disable_tqdm=False):
        N = len(list(range(start,stop,step)))
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
            _=list(tqdm.tqdm(pool.imap(func, zip(itertools.repeat(self), range(start,stop,step), range(N))),
                total=N, disable=disable_tqdm))
    
    def for_timepoint_single_thread(self, func:typing.Callable[[Experiment,int,int],None], start=0, stop=60000, step=600, disable_tqdm=False):
        N = len(list(range(start,stop,step)))
        _ = [func((self,tp, i)) for i, tp in tqdm.tqdm(enumerate(range(start,stop,step)), total=N, disable=disable_tqdm)]

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
def load_experiment(name:str, cls:typing.Type[Experiment]=Experiment):
    assert isinstance(name, str)
    
    # if Config.experiment_class is not None: Experiment = Config.experiment_class

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
    