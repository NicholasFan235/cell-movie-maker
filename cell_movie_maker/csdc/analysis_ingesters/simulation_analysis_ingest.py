import chaste_simulation_database_connector as csdc
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..analysis_ingest import AnalysisIngest
from ...analysers.simulation_analyser import SimulationAnalyser
import typing
import logging
import tqdm
import pathlib
import pandas as pd
import multiprocessing
import itertools


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def process_sim_json(info:tuple):
    sim:Simulation = info[0]
    analyser:typing.Type[SimulationAnalyser] = info[1]
    return dict(experiment=sim.name, iteration=sim.iteration, analysis_name=str(analyser), analysis_value=analyser.analyse(sim).to_json(), timestep=-1)

def process_sim_parquet(info:tuple):
    sim:Simulation = info[0]
    analyser:typing.Type[SimulationAnalyser] = info[1]
    return dict(experiment=sim.name, iteration=sim.iteration, analysis_name=str(analyser), analysis_value=analyser.analyse(sim).to_parquet(index=True), timestep=-1)

class SimulationAnalysisIngest(AnalysisIngest):
    """
    Class to analyse a simulation and write analysis to database.
    Can store data using parquet or json (parquet is significantly faster)
    '''

    Attributes
    ----------
    batch_size : int
        Number of simulations to process in each batch
    nproc : int
        Number of multiprocesses to use
    mode : str
        Data format to store to database (default = 'parquet')
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        
        Parameters
        ----------
        db : csdc.Connection
            Database connection
        skip_existing : bool, optional (default True)
            Skip analysis if analysis with matching metadata is already in database
        """
        super().__init__(*args, **kwargs)
        self.nproc = 50
        self.batch_size = 500
        self.mode:str = 'parquet'

    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[SimulationAnalyser])->None:
        """
        Perform analysis on simulation in experiment.  
        Timepoints are selected based on how this class is configured.

        Parameters
        ----------
        eperiment : Experiment
            Experiment containing simulations to process
        analyser : SimulationAnalyser
            SimulationAnalyser class which performs analysis on each Simulation
        
        Returns
        -------
        None
        """
        skip_sim_ids = self.get_skip_sims(experiment, str(analyser))
        process_sim = process_sim_json
        if self.mode == 'json': process_sim = process_sim_json
        elif self.mode == 'parquet': process_sim = process_sim_parquet
        else: raise RuntimeError(f'Mode \"{self.mode}\" not implemented, try "json" or "parquet"')

        for i, sims_batch in enumerate(chunk(experiment.sim_ids, self.batch_size)):
            to_process = [experiment.read_simulation(sim_id) for sim_id in sims_batch if sim_id not in skip_sim_ids]
            logging.info(f"Batch {i}, Performing {len(to_process)} new analysis...")
            with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
                analysis = list(tqdm.tqdm(
                    p.imap(process_sim, zip(to_process, itertools.repeat(analyser))),
                    total=len(to_process)))
            analysis = [r for r in analysis if r is not None]

            self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()
            
