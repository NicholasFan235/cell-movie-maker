import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
import numpy as np

import pandas as pd


class DeltaAnalyser(TimepointAnalyser):
    def __init__(self, delta:int, forward:bool=True):
        self.delta = delta
        self.forward=forward # Whether to calculate delta looking forward or backward from given timepoint
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        tp2 = simulation.read_timepoint((timepoint.timestep + self.delta) if self.forward else (max(0, timepoint.timestep - self.delta))).data.set_index('cell_id')[['x','y','damage']]
        tp1 = timepoint.data.set_index('cell_id')[['x', 'y', 'damage']]

        return (tp2-tp1 if self.forward else tp1-tp2).loc[tp1.index].rename(dict(x='delta_x', y='delta_y', damage='delta_damage'), axis=1).reset_index()

    def __str__(self):
        return f'Delta {self.delta/60:.0f}h'
