import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing

import pandas as pd


class TimepointAnalyser:
    def __init__(self):
        pass

    def analyse(self, timepoint:SimulationTimepoint)->pd.DataFrame|pd.Series|float|int:
        pass