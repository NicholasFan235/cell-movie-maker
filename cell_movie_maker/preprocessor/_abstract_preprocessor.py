from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ._abstract_analyser import AbstractAnalyser
from ..config import Config
import os
import pathlib
import numpy as np
import pandas as pd
from .count_analysers import TumourCount, TCellCount, BloodVesselCount
import tqdm


class AbstractPreprocessor:
    def __init__(self, output_parent_folder=None, name='info', make_folder_if_not_exists:bool=False):
        self.analysers = []
        self.name = name
        
        self.output_folder:pathlib.Path = Config.output_folder if output_parent_folder is None else pathlib.Path(output_parent_folder)
        if make_folder_if_not_exists: pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        if (not os.path.exists(self.output_folder)): raise FileNotFoundError(self.output_folder)

        # self.output_file = pathlib.Path(output_parent_folder, self.sim.name, self.sim.id, f'{name}.csv')
        # if not os.path.exists(self.output_file.parent):
        #     self.output_file.parent.mkdir(exist_ok=True, parents=True)

    def _process_internal(self, sim, start=0, stop=None, step=1, disable_tqdm=False):
        data = pd.DataFrame(columns=['timestep'] + [a.name for a in self.analysers], dtype=int).set_index('timestep')
        for t in tqdm.tqdm(sim.results_timesteps[start:stop:step], disable=disable_tqdm):
            tp = sim.read_timepoint(t)
            data.loc[t] = [analyser.analyse(tp, sim) for analyser in self.analysers]
        data.to_csv(self.output_folder.joinpath(sim.name, self.name, f'{sim.id}.csv'))

    def process(self, sim, start=0, stop=None, step=1, disable_tqdm=False):
        p = self.output_folder.joinpath(sim.name, self.name)
        if not p.exists(): p.mkdir(parents=True, exist_ok=True)
        self._process_internal(sim, start=start, stop=stop, step=step, disable_tqdm=disable_tqdm)

class Preprocessor(AbstractPreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analysers = [
            TumourCount(),
            TCellCount(),
            BloodVesselCount(),
        ]

    def process(self, sim, start=0, stop=None, step=1, disable_tqdm=False):
        super().process(sim, start=start, stop=stop, step=step, disable_tqdm=disable_tqdm)

    def add_analyser(self, analyser:AbstractAnalyser):
        self.analysers.append(analyser)
