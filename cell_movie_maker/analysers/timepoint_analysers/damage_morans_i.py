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
    def __init__(self, delta:int, forward:bool=True, network_type='Proximity', max_edge_distance=0.5):
        self.delta = delta
        self.forward = forward # Whether to use forward or backward looking damage
        self.delta_analyser = DeltaAnalyser(delta, forward)
        self.network_type=network_type
        self.max_edge_distance=max_edge_distance
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        import muspan as ms
        timepoint.append_analysis(self.delta_analyser)
        timepoint.data.loc[(timepoint.data.cell_type=='Tumour') & timepoint.data.delta_damage.isna(), 'delta_damage'] = 0
        domain = timepoint.to_muspan()
        morans = ms.spatial_statistics.morans_i(domain, ms.query.query(domain, 'cell_type', 'is', 'Tumour'), 'delta_damage', network_kwargs=dict(network_type=self.network_type, max_edge_distance=self.max_edge_distance))
        return pd.DataFrame({'z-score': [morans[0]], 'pvalue': [morans[1]]})

    def __str__(self):
        return f'{self.delta/60:.0f}h Damage Global Morans I {self.network_type}' + (f' {self.max_edge_distance}' if self.network_type == 'Proximity' else '') 
    
class BinaryDamageGlobalMoransIAnalyser(TimepointAnalyser):
    def __init__(self, delta:int, forward:bool=True, network_type='Proximity', max_edge_distance=0.5):
        self.delta = delta
        self.forward = forward # Whether to use forward or backward looking damage
        self.delta_analyser = DeltaAnalyser(delta, forward)
        self.network_type=network_type
        self.max_edge_distance=max_edge_distance
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation)->pd.DataFrame|pd.Series|float|int:
        import muspan as ms
        timepoint.append_analysis(self.delta_analyser)
        timepoint.data.loc[(timepoint.data.cell_type=='Tumour') & timepoint.data.delta_damage.isna(), 'delta_damage'] = 0
        timepoint.data['damaged'] = (timepoint.data.delta_damage>0).astype(float)
        domain = timepoint.to_muspan()
        morans = ms.spatial_statistics.morans_i(domain, ms.query.query(domain, 'cell_type', 'is', 'Tumour'), 'damaged', network_kwargs=dict(network_type=self.network_type, max_edge_distance=self.max_edge_distance))
        return pd.DataFrame({'z-score': [morans[0]], 'pvalue': [morans[1]]})

    def __str__(self):
        return f'{self.delta/60:.0f}h Binary Damage Global Morans I {self.network_type}' + (f' {self.max_edge_distance}' if self.network_type == 'Proximity' else '') 

class TumourDamageGlobalMoransIAnalyser(TimepointAnalyser):
    def __init__(self, network_type='Proximity', max_edge_distance=0.5):
        self.network_type=network_type
        self.max_edge_distance=max_edge_distance
    
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        import muspan as ms
        domain = timepoint.to_muspan()
        morans = ms.spatial_statistics.morans_i(domain, ms.query.query(domain, 'cell_type', 'is', 'Tumour'), 'damage', network_kwargs=dict(network_type=self.network_type, max_edge_distance=self.max_edge_distance))
        return pd.DataFrame({'z-score': [morans[0]], 'pvalue': [morans[1]]})

    def __str__(self):
        return f'Tumour Damage Global Morans I {self.network_type}' + (f' {self.max_edge_distance}' if self.network_type == 'Proximity' else '') 
    
