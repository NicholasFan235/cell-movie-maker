import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing

class AnalysisIngester:
    def __init__(self, db:csdc.ChasteDatabase):
        self.db:csdc.ChasteDatabase = db

    def ingest_experiment(self, experiment:Experiment, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_simulation(self, simulation:Simulation, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_timepoint(self, timepoint:SimulationTimepoint, *args, **kwargs):
        raise NotImplementedError
    
    