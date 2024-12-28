from __future__ import annotations
import chaste_simulation_database_connector as csdc
from ...experiment import Experiment
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


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def process_timepoint(info:tuple):
    tp:SimulationTimepoint = info[0]
    analyser:typing.Type[TimepointAnalyser] = info[1]
    experiment_name = info[2]
    try:
        return dict(experiment=experiment_name,
                    iteration=tp.id,
                    timestep=tp.timestep,
                    analysis_name=str(analyser),
                    analysis_value=analyser.analyse(tp).to_json())
    except RuntimeError as e:
        logging.debug(e)
        return None


class TimepointAnalysisIngest(AnalysisIngest):
    def __init__(self, *args, timestep_slice:slice=slice(None, None, -4), **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = 500
        self.timestep_slice = timestep_slice
        self.nproc = 50


    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[TimepointAnalyser]):
        skip_sim_timepoints = self.get_skip_sims(experiment, str(analyser))
        for i, sims_batch in enumerate(chunk(experiment.sim_ids, self.batch_size)):
            to_process = []
            logging.info(f"Batch {i}, Checking {len(sims_batch)} sims...")
            for sim_id in tqdm.tqdm(sims_batch):
                timesteps = set()
                sim = experiment.read_simulation(sim_id)
                for timestep in sim.results_timesteps[self.timestep_slice]:
                    if timestep > sim.results_timesteps[-1]: timestep = sim.results_timesteps[-1]
                    if (sim_id, timestep) not in skip_sim_timepoints:
                        timesteps.add(timestep)
                
                for timestep in timesteps:
                    to_process.append(sim.read_timepoint(timestep))

            logging.info(f"Batch {i}, Performing {len(to_process)} new analysis...")
            with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
                analysis = list(tqdm.tqdm(
                    p.imap(process_timepoint, zip(to_process, itertools.repeat(analyser), itertools.repeat(str(experiment)))),
                    total=len(to_process)))
            analysis = [r for r in analysis if r is not None]

            self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()

            
