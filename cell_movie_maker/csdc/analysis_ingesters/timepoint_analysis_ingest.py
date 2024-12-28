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
    return dict(experiment=experiment_name,
                iteration=tp.id,
                timestep=tp.timestep,
                analysis_name=str(analyser),
                analysis_value=analyser.analyse(tp).to_json())


class TimepointAnalysisIngest(AnalysisIngest):
    def __init__(self, *args, batch_size=500, timestep_slice:slice=slice(None, None, -4), **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.timestep_slice = timestep_slice


    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[TimepointAnalyser]):
        skip_sim_timepoints = self.get_skip_sims(experiment, str(analyser))
        for i, sims_batch in enumerate(chunk(experiment.simulations, self.batch_size)):
            to_process = [sim.read_timepoint(timestep) for sim in sims_batch
                          for timestep in sim.results_timesteps[self.timestep_slice]
                          if (sim.iteration, timestep) not in skip_sim_timepoints]
            logging.info(f"Batch {i}, Performing {len(to_process)} new analysis...")
            with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
                analysis = list(tqdm.tqdm(
                    p.imap(process_timepoint, zip(to_process, itertools.repeat(analyser), itertools.repeat(str(experiment)))),
                    total=len(to_process)))
            analysis = [r for r in analysis if r is not None]

            self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()

            
