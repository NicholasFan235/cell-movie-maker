from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint
from ..simulation import Simulation


class MeanTumourRadius(AbstractAnalyser):
    def __init__(self, name='mean_tumour_radius', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:SimulationTimepoint, sim=None):
        return tp.tumour_data.radius.mean()
    
class MedianTumourRadius(AbstractAnalyser):
    def __init__(self, name='median_tumour_radius', dtype=int, hypoxia_threshold=0.04):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return tp.tumour_data.radius.median()
