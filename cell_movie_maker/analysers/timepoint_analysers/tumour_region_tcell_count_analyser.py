import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
from ..helpers import alpha_shape_with_holes
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
        necrotic_threshold = self.necrotic_threshold if sim is None else sim.parameters['TumourNecroticConcentration']
        hypoxic_threshold = self.hypoxic_threshold if sim is None else sim.parameters['TumourHypoxicConcentration']

        tumour = timepoint.tumour_data

        necrotic_region = alpha_shape_with_holes(tumour.loc[tumour.oxygen < necrotic_threshold, ['x', 'y']].to_numpy(), alpha=self.alpha)[0]
        hypoxic_and_necrotic_region = alpha_shape_with_holes(tumour.loc[tumour.oxygen < hypoxic_threshold, ['x','y']].to_numpy(), alpha=self.alpha)[0]
        hypoxic_region = hypoxic_and_necrotic_region.difference(necrotic_region)
        tumour_region = alpha_shape_with_holes(tumour[['x','y']].to_numpy(), alpha=self.alpha)[0]
        normoxic_region = tumour_region.difference(hypoxic_and_necrotic_region)
        extended_tumour_region = tumour_region.buffer(self.buffer_size)
        buffer_region = extended_tumour_region.difference(tumour_region)

        width = 100 if sim is None else sim.parameters['WIDTH']
        height = 100 if sim is None else sim.parameters['HEIGHT']
        domain = shapely.Polygon([[0,0], [width,0], [width,height], [0, height]])
        exterior_region = domain.difference(extended_tumour_region)

        tcells = timepoint.cytotoxic_data[['x', 'y']].to_numpy()

        necrotic_region_count = int(shapely.contains_xy(necrotic_region, *tcells.T).sum())
        hypoxic_region_count = int(shapely.contains_xy(hypoxic_region, *tcells.T).sum())
        normoxic_region_count = int(shapely.contains_xy(normoxic_region, *tcells.T).sum())
        buffer_region_count = int(shapely.contains_xy(buffer_region, *tcells.T).sum())
        exterior_region_count = int(shapely.contains_xy(exterior_region, *tcells.T).sum())

        necrotic_region_density = 0 if necrotic_region.area <= 0 else necrotic_region_count / necrotic_region.area
        hypoxic_region_density = 0 if hypoxic_region.area <= 0 else hypoxic_region_count / hypoxic_region.area
        normoxic_region_density = 0 if normoxic_region.area <= 0 else normoxic_region_count / normoxic_region.area
        buffer_region_density = 0 if buffer_region.area <= 0 else buffer_region_count / buffer_region.area
        exterior_region_density = 0 if exterior_region.area <= 0 else exterior_region_count / exterior_region.area

        in_tumour_tcells = timepoint.cytotoxic_data.iloc[shapely.contains_xy(tumour_region, *tcells.T)]
        in_tumour_mean_potency = in_tumour_tcells['potency'].mean()
        in_tumour_mean_exhaustion = ((1-in_tumour_tcells['potency'])/sim.parameters['CD8InitialPotency']).mean()

        return dict(
            necrotic_region_count=necrotic_region_count, necrotic_region_density=necrotic_region_density,
            hypoxic_region_count=hypoxic_region_count, hypoxic_region_density=hypoxic_region_density,
            normoxic_region_count=normoxic_region_count, normoxic_region_density=normoxic_region_density,
            buffer_region_count=buffer_region_count, buffer_region_density=buffer_region_density,
            exterior_region_count=exterior_region_count, exterior_region_density=exterior_region_density,
            in_tumour_mean_potency=in_tumour_mean_potency,
            in_tumour_mean_exhaustion=in_tumour_mean_exhaustion
        )

    def __str__(self):
        return f'Tumour Region TCell Counts alpha={self.alpha:.2f} buffer_size={self.buffer_size}'
