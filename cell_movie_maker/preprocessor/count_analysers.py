from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint
from ..simulation import Simulation


class TumourCount(AbstractAnalyser):
    def __init__(self, name='n_tumour', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:SimulationTimepoint, sim=None):
        return int(tp.tumour_data.shape[0])
    
class HypoxicCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_hypoxic', dtype=int, hypoxia_threshold=0.04):
        super().__init__(name, dtype)
        self.hypoxia_threshold=hypoxia_threshold
        self.use_params_if_exists = True
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        if self.use_params_if_exists and sim is not None and sim.parameters is not None:
            if 'TumourHypoxicConcentration' in sim.parameters:
                return int(len(tp.tumour_data[tp.tumour_data.oxygen < sim.parameters['TumourHypoxicConcentration']]))
        return int(len(tp.tumour_data[tp.tumour_data.oxygen < self.hypoxia_threshold]))

class NecroticCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_necrotic', dtype=int, necrosis_threshold=0.01):
        super().__init__(name, dtype)
        self.necrosis_threshold=necrosis_threshold
        self.use_params_if_exists = True
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        if self.use_params_if_exists and sim is not None and sim.parameters is not None:
            if 'TumourNecroticConcentration' in sim.parameters:
                return int(len(tp.tumour_data[tp.tumour_data.oxygen < sim.parameters['TumourNecroticConcentration']]))
        return int(len(tp.tumour_data[tp.tumour_data.oxygen < self.necrosis_threshold]))

class TCellCount(AbstractAnalyser):
    def __init__(self, name='n_tcells', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return int(tp.cytotoxic_data.shape[0])
    
class TCellPotencyCount(AbstractAnalyser):
    def __init__(self, name='n_tcells_potency_le', dtype=int, potency_percent=90):
        super().__init__(name + str(potency_percent), dtype)
        self.threshold = potency_percent
        self.use_params_if_exists = True
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        t = self.threshold/100
        if self.use_params_if_exists:
            t = sim.parameters['CD8InitialPotency']*t
        return int(len(tp.cytotoxic_data[tp.cytotoxic_data.potency <= t]))
    
class MeanTCellPotency(AbstractAnalyser):
    def __init__(self, name='avg_tcell_potency', dtype=float):
        super().__init__(name, dtype)
        self.use_params_if_exists = True
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return tp.cytotoxic_data['potency'].mean()
    
class MeanTCellExhaustion(AbstractAnalyser):
    def __init__(self, name='avg_tcell_exhaustion', dtype=float):
        super().__init__(name, dtype)
        self.use_params_if_exists = True
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        initial_potency = sim.parameters['CD8InitialPotency'] if sim is not None else 1
        return ((1-tp.cytotoxic_data['potency']/initial_potency)).mean()

class TumourDamageCount(AbstractAnalyser):
    def __init__(self, name='n_tumour_damage_gt', dtype=int, damage_percent=90):
        super().__init__(name + str(damage_percent), dtype)
        self.threshold = damage_percent
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return int(len(tp.tumour_data[tp.tumour_data.damage*100 > self.threshold]))
    
class BloodVesselCount(AbstractAnalyser):
    def __init__(self, name='n_vessels', dtype=int):
        super().__init__(name, dtype)
    
    def analyse(self, tp:SimulationTimepoint, sim=None):
        return int(len(tp.blood_vessel_data[tp.blood_vessel_data.target_radius > 0]))

class BloodVesselRadiusCount(AbstractAnalyser):
    def __init__(self, name='n_vessels_radius_ge', dtype=int, radius_percent_threshold=90):
        super().__init__(name + str(radius_percent_threshold), dtype)
        self.threshold = radius_percent_threshold
        self.use_params_if_exists = True
    
    def analyse(self, tp:Simulation, sim=None):
        if self.use_params_if_exists and sim is not None and sim.parameters is not None:
            if 'VesselMaxRadius' in sim.parameters and 'VesselMinRadius' in sim.parameters:
                t = sim.parameters['VesselMinRadius'] + self.threshold/100 * (sim.parameters['VesselMaxRadius'] - sim.parameters['VesselMinRadius'])
                return int(len(tp.blood_vessel_data[tp.blood_vessel_data.target_radius >= t]))
        return int(len(tp.blood_vessel_data[tp.blood_vessel_data.target_radius > self.threshold/100]))

