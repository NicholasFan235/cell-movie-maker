from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint


class TumourCount(AbstractAnalyser):
    def __init__(self, name='n_tumour', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:SimulationTimepoint):
        return int(tp.tumour_data.shape[0])
    
class TCellCount(AbstractAnalyser):
    def __init__(self, name='n_t-cells', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint):
        return int(tp.cytotoxic_data.shape[0])
    
class BloodVesselCount(AbstractAnalyser):
    def __init__(self, name='vessels', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint):
        return int(tp.cytotoxic_data.shape[0])

