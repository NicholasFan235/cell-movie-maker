import chaste_simulation_database_connector as csdc
from ...experiment import Experiment
from ..analysis_ingest import AnalysisIngest
from ...analysers.timepoint_analyser import TimepointAnalyser
import typing
import logging
import tqdm
import pathlib
import pandas as pd


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

class TimepointAnalysisIngest(AnalysisIngest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def ingest_experiment(self, experiment:Experiment, analyser:typing.Type[TimepointAnalyser]):
        raise NotImplementedError

            
