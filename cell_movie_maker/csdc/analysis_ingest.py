import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing
import pandas as pd

class AnalysisIngest:
    def __init__(self, db:csdc.Connection, skip_existing=True):
        self.db:csdc.Connection = db
        self.skip_existing = skip_existing

    def ingest_experiment(self, experiment:Experiment, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_simulation(self, simulation:Simulation, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_timepoint(self, timepoint:SimulationTimepoint, *args, **kwargs):
        raise NotImplementedError
    
    def get_skip_sims(self, experiment:Experiment, analysis_name:str):
        if not self.skip_existing: return set()
        experiment = str(experiment)
        skip_ids = pd.read_sql("SELECT iteration FROM analysis INNER JOIN simulations ON analysis.simulation_id = simulations.id WHERE analysis_name = :analysis_name AND experiment = :experiment",
                    self.db.get_connection(), params=dict(analysis_name = analysis_name, experiment=experiment))
        self.db.close_connection()
        return set(skip_ids.iteration)