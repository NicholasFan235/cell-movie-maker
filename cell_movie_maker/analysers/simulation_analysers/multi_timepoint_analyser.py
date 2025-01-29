import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
import typing
import enum
import multiprocessing
import tqdm
import numpy as np

import pandas as pd


class MultiTimepointAnalyser(SimulationAnalyser):
    def __init__(self, timepoint_analyser:typing.Type[TimepointAnalyser], timepoint_slice:slice=slice(None)):
        self.timepoint_analyser:typing.Type[TimepointAnalyser] = timepoint_analyser
        self.timepoint_slice = timepoint_slice
        
    def analyse(self, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        df = []
        for timestep in simulation.results_timesteps[self.timepoint_slice]:
            tp = simulation.read_timepoint(timestep)
            df.append(dict(timestep=timestep, **self.timepoint_analyser.analyse(tp, simulation)))
        return pd.DataFrame(df).set_index('timestep')

    def __str__(self):
        return str(self.timepoint_analyser)
