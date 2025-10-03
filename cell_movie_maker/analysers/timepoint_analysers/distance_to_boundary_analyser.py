import chaste_simulation_database_connector as csdc
from ..simulation_analyser import SimulationAnalyser
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..timepoint_analyser import TimepointAnalyser
from .delta_analyser import DeltaAnalyser
from ..helpers import alpha_shape
import numpy as np
import shapely

import pandas as pd


class TumourDistanceToBoundaryAnalyser(TimepointAnalyser):
    def __init__(self, alpha:float=0.5):
        self.alpha = alpha
        
    def analyse(self, timepoint:SimulationTimepoint, simulation:Simulation=None)->pd.DataFrame|pd.Series|float|int:
        shape = alpha_shape(timepoint.tumour_data[['x','y']].to_numpy(), alpha=self.alpha)
                
        distances = shape[0].boundary.distance([shapely.Point(p) for p in timepoint.data[['x','y']].to_numpy()])
        contains = shapely.contains_xy(shape[0], timepoint.data['x'].to_numpy(), timepoint.data['y'].to_numpy())
        distances[contains<=0] *= -1

        return pd.DataFrame({'cell_id':timepoint.data['cell_id'].to_numpy(), 'boundary_dist':distances})

    def __str__(self):
        return f'Tumour distance to boundary'

class TumourBoundaryDistanceDistributionAnalyser(TimepointAnalyser):
    def __init__(self, alpha=0.5, delta=24*60, forward:bool=True, dist_bins=np.linspace(0,20,51)):
        self.alpha = alpha
        self.delta = delta
        self.dist_bins = dist_bins
        self.boundary_distance_analyser = TumourDistanceToBoundaryAnalyser(alpha=alpha)
        self.delta_analyser = DeltaAnalyser(delta=delta, forward=forward)

    def analyse(self, timepoint:SimulationTimepoint, sim:Simulation=None):
        timepoint.append_analysis(self.boundary_distance_analyser)
        timepoint.append_analysis(self.delta_analyser)
        data = timepoint.data
        data['boundary_dist_bin'] = pd.cut(data['boundary_dist'], bins=self.dist_bins, labels=self.dist_bins[:-1])
        
        d = data.groupby('boundary_dist_bin')[['oxygen', 'radius', 'pressure', 'tissue_stress']].mean()
        td = data[data.cell_type == 'Tumour'].groupby('boundary_dist_bin')[['delta_damage', 'damage', 'oxygen', 'radius', 'pressure', 'tissue_stress']].mean()
        cd = data[data.cell_type == 'T Cell'].groupby('boundary_dist_bin')[['potency', 'exhaustion %']].mean()
        bd = data[data.cell_type == 'Blood Vessel'].query('target_radius > 0').groupby('boundary_dist_bin')[['radius', 'pressure', 'tissue_stress']].mean()

        return d.join(td, rsuffix='_tumour').join(cd, rsuffix='_tcell').join(bd, rsuffix='_vessel').reset_index()

    def __str__(self):
        return f'Tumour boundary distance distribution'