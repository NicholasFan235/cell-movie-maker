from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint
from ..simulation import Simulation


class MeanTumourOxygen(AbstractAnalyser):
    def __init__(self, name='mean_tumour_oxygen', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:SimulationTimepoint, sim=None):
        return tp.tumour_data.oxygen.mean()
    
class MedianTumourOxygen(AbstractAnalyser):
    def __init__(self, name='median_tumour_oxygen', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return tp.tumour_data.oxygen.median()
