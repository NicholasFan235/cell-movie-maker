import chaste_simulation_database_connector as csdc
from ...experiment import Experiment
from ...simulation import Simulation
from ...simulation_timepoint import SimulationTimepoint
from ..analysis_ingest import AnalysisIngest
from ...config import Config
import typing
import logging
import tqdm
import pathlib
import pandas as pd


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

class InfoIngester(AnalysisIngest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def ingest_experiment(self, experiment:Experiment, batch_size:int=None, disable_tqdm:bool=False):
        is_batched:bool = batch_size != None
        if batch_size is None: batch_size = len(experiment.sim_ids)
        for i, sims_batch in enumerate(chunk(experiment.sim_ids, batch_size)):
            if is_batched: logging.info(f"Batch {i}...")
            self.db.add_bulk_simulations([dict(experiment=experiment.name, iteration=int(sim_id)) for sim_id in sims_batch], commit=True, close_connection=True)
            results = []
            for sim_id in tqdm.tqdm(sims_batch, disable=disable_tqdm):
                info_file = Config.output_folder.joinpath(experiment.name, "info", f'sim_{sim_id}.csv')
                if not info_file.exists(): continue
                info = pd.read_csv(info_file, index_col='timestep')
                results.append(dict(experiment=experiment.name, iteration=sim_id, timestep=None, analysis_name="cellcounts", analysis_value=info.to_json()))
            self.db.add_bulk_analysis(results, commit=True, close_connection=True)
        self.db.commit()
        self.db.close_connection()
            
