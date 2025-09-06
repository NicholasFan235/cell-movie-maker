import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
from .delta_analyser import DeltaAnalyser
from ..helpers import morans_i
import typing
import enum
import multiprocessing
import tqdm
import numpy as np

import pandas as pd


class DamageGlobalMoransIAnalyser(TimepointAnalyser):
    def __init__(self, delta:int, forward:bool=True, distances:list[int]=[0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]):
        self.delta = delta
        self.forward = forward # Whether to use forward or backward looking damage
        self.delta_analyser = DeltaAnalyser(delta, forward)
        self.distances = distances
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        data = timepoint.tumour_data.set_index('cell_id').join(self.delta_analyser.analyse(timepoint, simulation).set_index('cell_id'), how='left')
        return morans_i(data[['x','y']].to_numpy(), data['delta_damage'].fillna(0).to_numpy(), self.distances).T

    def __str__(self):
        return f'{self.delta/60:.0f}h Damage Global Morans I'
    
class BinaryDamageGlobalMoransIAnalyser(TimepointAnalyser):
    def __init__(self, delta:int, forward:bool=True, distances:list[int]=[0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]):
        self.delta = delta
        self.forward = forward # Whether to use forward or backward looking damage
        self.delta_analyser = DeltaAnalyser(delta, forward)
        self.distances = distances
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        data = timepoint.tumour_data.set_index('cell_id').join(self.delta_analyser.analyse(timepoint, simulation).set_index('cell_id'), how='left')
        return morans_i(data[['x','y']].to_numpy(), (data['delta_damage'].fillna(0).to_numpy()>0).astype(int), self.distances).T

    def __str__(self):
        return f'{self.delta/60:.0f}h Binary Damage Global Morans I'

class TumourDamageGlobalMoransIAnalyser(TimepointAnalyser):
    def __init__(self, distances:list[int]=[0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]):
        self.distances = distances
    
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        data = timepoint.tumour_data
        return morans_i(data[['x','y']].to_numpy(), data['damage'].fillna(0).to_numpy(), self.distances).T

    def __str__(self):
        return f'Tumour Damage Global Morans I'