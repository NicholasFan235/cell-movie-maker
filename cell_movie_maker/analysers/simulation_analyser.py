import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing
import enum
import multiprocessing
import tqdm

import pandas as pd


class SimulationAnalyser:
    class ParallelismMode(enum.Enum):
        NONE=1
        SIMULATIONS=2
        TIMEPOINTS=3

    def __init__(self):
        self.parallelism_mode = SimulationAnalyser.ParallelismMode.SIMULATIONS
        self.timepoint_slice = slice(None)
        self.simulation_batch_size = 500
        self.timepoint_batch_size = 200
        self.nproc = 16

    def analyse_timepoint(self, timepoint:SimulationTimepoint, **kwargs)->pd.DataFrame|pd.Series|float|int:
        raise NotImplementedError

    def analyse_simulation(self, simulation:Simulation, **kwargs)->pd.DataFrame|pd.Series|float|int:
        match self.parallelism_mode:
            case SimulationAnalyser.ParallelismMode.TIMEPOINTS:
                with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as pool:
                    return list(tqdm.tqdm(pool.imap(self.analyse_timepoint, simulation[self.timepoint_slice]), total=len(simulation.results_timesteps[self.timepoint_slice])))
            case _:
                return [self.analyse_timepoint(tp) for tp in tqdm.tqdm(simulation[self.timepoint_slice], total=len(simulation.results_timesteps[self.timepoint_slice]))]

    def analyse_experiment(self, experiment:Experiment, **kwargs):
        match self.parallelism_mode:
            case SimulationAnalyser.ParallelismMode.Simulations:
                pass
            case _:
                pass

    def experiment_analysis(self, experiment:Experiment, **kwargs):
        pass
    