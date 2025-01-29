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


class TumourRegionSizesAnalyser(TimepointAnalyser):
    def __init__(self, alpha:float=.5):
        self.alpha = alpha
        self.hypoxic_threshold = 0.1
        
    def analyse(self, timepoint:SimulationTimepoint, sim:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        hypoxic_threshold = self.hypoxic_threshold if sim is None else sim.parameters['TumourHypoxicThreshold']
        hypoxic_cells = timepoint.tumour_data[timepoint.tumour_data.oxygen <= hypoxic_threshold]

        hypoxic_region = alpha_shape(hypoxic_cells[['x','y']].to_numpy(), alpha=self.alpha)[0]
        tumour_region = alpha_shape(timepoint.tumour_data[['x','y']].to_numpy(), alpha=self.alpha)[0]
        normoxic_region = tumour_region.difference(hypoxic_region)
        
        return dict(tumour_area=tumour_region.area, hypoxic_area=hypoxic_region.area, normoxic_area=normoxic_region.area)

    def __str__(self):
        return f'Tumour Region Sizes alpha={self.alpha:.2f}'
