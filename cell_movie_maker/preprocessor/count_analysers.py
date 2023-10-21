from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint


class TumourCount(AbstractAnalyser):
    def __init__(self, name='n_tumour', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:SimulationTimepoint):
        return int(tp.tumour_data.shape[0])
    
class HypoxicCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_hypoxic', dtype=int, hypoxia_threshold=0.04):
        super().__init__(name, dtype)
        self.hypoxia_threshold=hypoxia_threshold
    
    def analyse(self, tp:SimulationTimepoint):
        return int(len(tp.tumour_data[tp.tumour_data.oxygen < self.hypoxia_threshold]))

class NecroticCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_necrotic', dtype=int, necrosis_threshold=0.01):
        super().__init__(name, dtype)
        self.necrosis_threshold=necrosis_threshold
    
    def analyse(self, tp:SimulationTimepoint):
        return int(len(tp.tumour_data[tp.tumour_data.oxygen < self.necrosis_threshold]))

class TCellCount(AbstractAnalyser):
    def __init__(self, name='n_t-cells', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint):
        return int(tp.cytotoxic_data.shape[0])
    
class TCellPotencyCount(AbstractAnalyser):
    def __init__(self, name='n_t-cells_potency', dtype=int, potency_percent=90):
        super().__init__(name + str(potency_percent), dtype)
        self.threshold = potency_percent
    
    def analyse(self, tp:SimulationTimepoint):
        return int(len(tp.cytotoxic_data[tp.cytotoxic_data.potency*100 < self.threshold]))

class TumourDamageCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_damage', dtype=int, damage_percent=90):
        super().__init__(name + str(damage_percent), dtype)
        self.threshold = damage_percent
    
    def analyse(self, tp:SimulationTimepoint):
        return int(len(tp.tumour_data[tp.tumour_data.damage*100 > self.threshold]))
    
class BloodVesselCount(AbstractAnalyser):
    def __init__(self, name='vessels', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint):
        return int(tp.cytotoxic_data.shape[0])

