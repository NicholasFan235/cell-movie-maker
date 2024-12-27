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

class TimepointAnalysisIngester(AnalysisIngest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

            
