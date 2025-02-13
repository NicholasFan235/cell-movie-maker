import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
from ..helpers import alpha_shape, alpha_shape_with_holes
import typing
import enum
import multiprocessing
import tqdm
import numpy as np

import pandas as pd


class TumourRegionSizesAnalyser(TimepointAnalyser):
    def __init__(self, alpha:float=.5):
        self.alpha = alpha
        self.necrotic_threshold = 0
        self.hypoxic_threshold = 0.1
        
    def analyse(self, timepoint:SimulationTimepoint, sim:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        necrotic_threshold = self.necrotic_threshold if sim is None else sim.parameters['TumourNecroticConcentration']
        hypoxic_threshold = self.hypoxic_threshold if sim is None else sim.parameters['TumourHypoxicConcentration']

        tumour = timepoint.tumour_data

        necrotic_region = alpha_shape_with_holes(tumour.loc[tumour.oxygen < necrotic_threshold, ['x', 'y']].to_numpy(), alpha=self.alpha)[0]
        hypoxic_and_necrotic_region = alpha_shape_with_holes(tumour.loc[tumour.oxygen < hypoxic_threshold, ['x','y']].to_numpy(), alpha=self.alpha)[0]
        hypoxic_region = hypoxic_and_necrotic_region.difference(necrotic_region)
        tumour_region = alpha_shape_with_holes(tumour[['x','y']].to_numpy(), alpha=self.alpha)[0]
        normoxic_region = tumour_region.difference(hypoxic_and_necrotic_region)
        
        return dict(tumour_area=tumour_region.area, normoxic_area=normoxic_region.area, hypoxic_area=hypoxic_region.area, necrotic_area=necrotic_region.area)

    def __str__(self):
        return f'Tumour Region Sizes alpha={self.alpha:.2f}'
