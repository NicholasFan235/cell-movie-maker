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


class RoundnessAnalyser(TimepointAnalyser):
    def __init__(self, alpha:float=.5):
        self.alpha = alpha
        
    def analyse(self, timepoint:SimulationTimepoint, sim:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        hull, edge_points = alpha_shape(timepoint.tumour_data[['x', 'y']].to_numpy(), alpha=self.alpha)
        roundness = hull.area * 4 * np.pi / (hull.length * hull.length) if hull.length > 0 else 0
        return dict(roundness=roundness)

    def __str__(self):
        return f'Roundness alpha={self.alpha:.2f}'
