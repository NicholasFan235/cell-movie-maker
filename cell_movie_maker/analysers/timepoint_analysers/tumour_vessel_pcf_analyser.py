import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
from ..helpers import alpha_shape
import typing
import enum
import multiprocessing
import tqdm
import numpy as np

import pandas as pd


class TumourVesselPCFAnalyser(TimepointAnalyser):
    def __init__(self, r_max=50, dr=1, step=1):
        self.r_max = r_max
        self.dr = dr
        self.step = step
        
    def analyse(self, timepoint:SimulationTimepoint)->pd.DataFrame|pd.Series|float|int:
        import muspan as ms
        domain = timepoint.to_muspan()
        r,g = ms.spatial_statistics.cross_pair_correlation_function(
            domain,
            ms.query.query(domain, "celltype", "is", "Tumour"),
            ms.query.query(domain, "celltype", "is", "Vessel"),
            max_R = self.r_max, annulus_width=self.dr, annulus_step=self.step)
        return pd.DataFrame.from_dict({'r':r, 'g':g}, orient='columns')

    def __str__(self):
        return f'Tumour-Vessel PCF r={self.r_max} dr={self.dr} step={self.step}'
