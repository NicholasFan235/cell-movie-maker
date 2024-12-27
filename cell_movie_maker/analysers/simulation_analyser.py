import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
import typing

import pandas as pd


class SimulationAnalyser:
    def __init__(self):
        pass

    def analyse(self, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        pass
    

    