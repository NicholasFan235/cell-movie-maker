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
import shapely

import pandas as pd


class TumourRegionTCellCountAnalyser(TimepointAnalyser):
    def __init__(self, alpha:float=.5):
        self.alpha = alpha
        self.hypoxic_threshold = .1
        self.buffer_size = 5
        
    def analyse(self, timepoint:SimulationTimepoint, sim:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        hypoxic_threshold = self.hypoxic_threshold if sim is None else sim.parameters['TumourHypoxicThreshold']
        hypoxic_cells = timepoint.tumour_data[timepoint.tumour_data.oxygen <= hypoxic_threshold]

        hypoxic_region = alpha_shape(hypoxic_cells[['x','y']].to_numpy(), alpha=self.alpha)[0]
        tumour_region = alpha_shape(timepoint.tumour_data[['x','y']].to_numpy(), alpha=self.alpha)[0]
        normoxic_region = tumour_region.difference(hypoxic_region)
        extended_tumour_region = tumour_region.buffer(self.buffer_size)
        buffer_region = extended_tumour_region.difference(tumour_region)

        width = 100 if sim is None else sim.parameters['WIDTH']
        height = 100 if sim is None else sim.paraemetrs['HEIGHT']
        domain = shapely.Polygon([[0,0], [width,0], [width,height], [0, height]])
        exterior_region = domain.difference(extended_tumour_region)

        tcells = timepoint.cytotoxic_data[['x', 'y']].to_numpy()

        hypoxic_region_count = int(shapely.contains_xy(hypoxic_region, *tcells.T).sum())
        normoxic_region_count = int(shapely.contains_xy(normoxic_region, *tcells.T).sum())
        buffer_region_count = int(shapely.contains_xy(buffer_region, *tcells.T).sum())
        exterior_region_count = int(shapely.contains_xy(exterior_region, *tcells.T).sum())

        hypoxic_region_density = 0 if hypoxic_region.area <= 0 else hypoxic_region_count / hypoxic_region.area
        normoxic_region_density = 0 if normoxic_region.area <= 0 else normoxic_region_count / normoxic_region.area
        buffer_region_density = 0 if buffer_region.area <= 0 else buffer_region_count / buffer_region.area
        exterior_region_density = 0 if exterior_region.area <= 0 else exterior_region_count / exterior_region.area

        return dict(
            hypoxic_region_count=hypoxic_region_count, hypoxic_region_density=hypoxic_region_density,
            normoxic_region_count=normoxic_region_count, normoxic_region_density=normoxic_region_density,
            buffer_region_count=buffer_region_count, buffer_region_density=buffer_region_density,
            exterior_region_count=exterior_region_count, exterior_region_density=exterior_region_density
        )

    def __str__(self):
        return f'Tumour Region TCell Counts alpha={self.alpha:.2f} buffer_size={self.buffer_size}'
