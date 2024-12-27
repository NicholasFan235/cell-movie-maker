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


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

def process_sim(sim:Simulation, analyser:typing.Type[SimulationAnalyser]):
    return dict(experiment=sim.name, iteration=sim.iteration, analysis_name=str(analyser), analysis_value=analyser.analyse(sim))

class SimulationAnalysisIngest(AnalysisIngest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nproc = 50
        self.batch_size = 500


    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[SimulationAnalyser]):
        for i, sims_batch in chunk(experiment.sim_ids, self.batch_size):
            logging.info(f"Batch {i}...")
            with multiprocessing.Pool(self.nproc, maxtasksperchild=1) as p:
                analysis = list(tqdm.tqdm(
                    p.imap(lambda it: process_sim(experiment.read_simulation(it), analyser), sims_batch),
                    total=len(experiment.sim_ids)))
            analysis = [r for r in analysis if r is not None]

            self.db.add_bulk_analysis(analysis, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()
            
