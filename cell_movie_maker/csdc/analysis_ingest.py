import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing
import pandas as pd

class AnalysisIngest:
    """
    Abstract class to handle performing and storing analysis to a database

    Attributes
    ----------
    db : csdc.Connection
        CSDC Database connection
    skip_existing : bool
        If true will skip performing analysis if analysis already exists in database
    """
    def __init__(self, db:csdc.Connection, skip_existing=True):
        """
        Constructor
        
        Parameters
        ----------
        db : csdc.Connection
            Database connection
        skip_existing : bool, optional (default True)
            Skip analysis if analysis with matching metadata is already in database
        """
        self.db:csdc.Connection = db
        self.skip_existing = skip_existing

    def ingest_experiment(self, experiment:Experiment, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_simulation(self, simulation:Simulation, *args, **kwargs):
        raise NotImplementedError
    
    def ingest_timepoint(self, timepoint:SimulationTimepoint, *args, **kwargs):
        raise NotImplementedError
    
    def get_skip_sims(self, experiment:Experiment, analysis_name:str)->set[int]:
        """
        Find simulations in experiment where there is already analysis with name analysis_name

        Parameters
        ----------
        experiment: Experiment, str
            Experiment to check
        analysis_name: str
            Name of analysis
        
        Returns
        -------
        set[int]
            Set of simulation ids for which there is existing analysis matching analysis_name
        """
        if not self.skip_existing: return set()
        experiment = str(experiment)
        skip_ids = pd.read_sql("SELECT iteration FROM analysis INNER JOIN simulations ON analysis.simulation_id = simulations.id WHERE analysis_name = :analysis_name AND experiment = :experiment",
                    self.db.get_connection(), params=dict(analysis_name = analysis_name, experiment=experiment))
        self.db.close_connection()
        return set(skip_ids.iteration)
    
    def get_skip_sim_timepoints(self, experiment:Experiment, analysis_name:str)->set[tuple[int,int]]:
        """
        Find simulation timepoints in experiment where there is already analysis with name analysis_name

        Parameters
        ----------
        experiment: Experiment, str
            Experiment to check
        analysis_name: str
            Name of analysis
        
        Returns
        -------
        set[int]
            Set of (simulation id, timestep) for which there is existing analysis matching analysis_name
        """
        if not self.skip_existing: return set()
        experiment = str(experiment)
        skip_ids = pd.read_sql("SELECT iteration, timestep FROM analysis INNER JOIN simulations ON analysis.simulation_id = simulations.id WHERE analysis_name = :analysis_name AND experiment = :experiment",
                    self.db.get_connection(), params=dict(analysis_name = analysis_name, experiment=experiment))
        self.db.close_connection()
        return {(int(r[0]), int(r[1])) for _,r in skip_ids.iterrows()}
    