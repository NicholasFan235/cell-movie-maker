from __future__ import annotations
import chaste_simulation_database_connector as csdc
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..analysis_ingest import AnalysisIngest
from ...analysers.timepoint_analyser import TimepointAnalyser
import typing
import logging
import tqdm
import pathlib
import pandas as pd
import enum
import multiprocessing
import itertools
import logging


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def process_timepoint_json(info:tuple):
    tp:SimulationTimepoint = info[0]
    analyser:typing.Type[TimepointAnalyser] = info[1]
    experiment_name = info[2]
    try:
        return dict(experiment=experiment_name,
                    iteration=int(tp.id.lstrip('sim_')),
                    timestep=tp.timestep,
                    analysis_name=str(analyser),
                    analysis_value=analyser.analyse(tp, tp.sim).to_json())
    except Exception as e:
        logging.debug(e)
        return None
    
def process_timepoint_parquet(info:tuple):
    tp:SimulationTimepoint = info[0]
    analyser:typing.Type[TimepointAnalyser] = info[1]
    experiment_name = info[2]
    try:
        return dict(experiment=experiment_name,
                    iteration=int(tp.id.lstrip('sim_')),
                    timestep=tp.timestep,
                    analysis_name=str(analyser),
                    analysis_value=analyser.analyse(tp, tp.sim).to_parquet(index=True))
    except Exception as e:
        logging.debug(e)
        return None


class TimepointAnalysisIngest(AnalysisIngest):
    """
    Class to analyse a slice of timepoints from simulations and write analysis to database.
    Can store data using parquet or json (parquet is significantly faster)
    '''

    Attributes
    ----------
    timestep_slice : slice
        Slice which specifies which timesteps to process in each simulation
    batch_size : int
        Number of simulations to process in each batch
    nproc : int
        Number of multiprocesses to use
    mode : str
        Data format to store to database (default = 'parquet')
    """
    def __init__(self, *args, timestep_slice:slice=slice(None, None, -4), **kwargs):
        """
        Constructor
        
        Parameters
        ----------
        db : csdc.Connection
            Database connection
        timestep_slice : slice
            Slice that specifies which timesteps to process in each simulation
        skip_existing : bool, optional (default True)
            Skip analysis if analysis with matching metadata is already in database
        """
        super().__init__(*args, **kwargs)
        self.batch_size = 500
        self.timestep_slice = timestep_slice
        self.nproc = 50
        self.mode:str = 'parquet'


    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[TimepointAnalyser])->None:
        """
        Perform analysis on simulation timepoints in experiment.  
        Timepoints are selected based on how this class is configured.

        Parameters
        ----------
        eperiment : Experiment
            Experiment containing simulations to process
        analyser : TimepointAnalyser
            TimepointAnalyser class which performs analysis on each SimulationTimepoint
        
        Returns
        -------
        None
        """
        skip_sim_timepoints = self.get_skip_sim_timepoints(experiment, str(analyser))
        if self.mode == 'json': process_timepoint = process_timepoint_json
        elif self.mode == 'parquet': process_timepoint = process_timepoint_parquet
        else: raise RuntimeError(f'Mode \"{self.mode}\" not implemented, try "json" or "parquet"')

        for i, sims_batch in enumerate(chunk(experiment.sim_ids, self.batch_size)):
            to_process = []
            logging.info(f"Batch {i} / {len(experiment.sim_ids)//self.batch_size+1}")
            # logging.info(f"Batch {i}, Checking {len(sims_batch)} sims...")
            for sim_id in tqdm.tqdm(sims_batch, desc="Checking sim batch"):
                timesteps = set()
                sim = experiment.read_simulation(sim_id)
                for timestep in sim.results_timesteps[self.timestep_slice]:
                    if timestep > sim.results_timesteps[-1]: timestep = sim.results_timesteps[-1]
                    if self.skip_existing and (sim_id, timestep) in skip_sim_timepoints: continue
                    timesteps.add(timestep)
                
                for timestep in timesteps:
                    try:
                        tp = sim.read_timepoint(timestep)
                        if tp.ok: to_process.append(tp)
                    except Exception as e:
                        logging.error(f"Unable to process sim_{sim_id} {timestep}")

            logging.info(f"Batch {i}, Performing {len(to_process)} new analysis...")
            with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
                analysis = list(tqdm.tqdm(
                    p.imap(process_timepoint, zip(to_process, itertools.repeat(analyser), itertools.repeat(str(experiment)))),
                    total=len(to_process), desc="Performing analysis"))
            analysis = [r for r in analysis if r is not None]

            logging.info(f"Batch {i}, Inserting {len(analysis)} new analysis...")
            self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()

    def ingest_simulation(self, sim:Simulation, analyser:typing.Type[TimepointAnalyser])->None:
        """
        Perform analysis on simulation timepoints in a simulation.  
        Timepoints are selected based on how this class is configured.

        Parameters
        ----------
        sim : Simulation
            Simulation to process
        analyser : TimepointAnalyser
            TimepointAnalyser class which performs analysis on each SimulationTimepoint
        
        Returns
        -------
        None
        """
        skip_sim_timepoints = self.get_skip_sim_timepoints(sim.name, str(analyser))
        if self.mode == 'json': process_timepoint = process_timepoint_json
        elif self.mode == 'parquet': process_timepoint = process_timepoint_parquet
        else: raise RuntimeError(f'Mode \"{self.mode}\" not implemented, try "json" or "parquet"')

        timepoints = []
        for timestep in sim.results_timesteps[self.timestep_slice]:
            if timestep > sim.results_timesteps[-1]: timestep = sim.results_timesteps[-1]
            if self.skip_existing and (sim.iteration, timestep) in skip_sim_timepoints: continue
            timepoints.append(sim.read_timepoint(timestep))

        with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
            analysis = list(tqdm.tqdm(
                p.imap(process_timepoint, zip(timepoints, itertools.repeat(analyser), itertools.repeat(str(sim.name)))),
                total=len(timepoints), desc="Performing analysis"))
        analysis = [r for r in analysis if r is not None]

        logging.info(f"Inserting {len(analysis)} new analysis...")
        self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()


            
