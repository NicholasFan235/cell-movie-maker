from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import SimulationTimepoint
from ..simulation import Simulation




class TotalVascularisation(AbstractAnalyser):
    def __init__(self, name='vascularisation', dtype=float):
        super().__init__(name, dtype)
        self.use_params_if_exists = True
    
    def analyse(self, tp:Simulation, sim=None):
        assert sim is not None
        assert 'VesselMaxRadius' in sim.parameters
        assert 'VesselMinRadius' in sim.parameters
        radii = tp.blood_vessel_data[tp.blood_vessel_data['target_radius']>0]['radius']
        a,b = sim.parameters['VesselMinRadius'], sim.parameters['VesselMaxRadius']
        return ((radii - a)/(b-a)).sum()
