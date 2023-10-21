from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from ._abstract_analyser import AbstractAnalyser
import os
import pathlib
import numpy as np
import pandas as pd
from .count_analysers import TumourCount, TCellCount, BloodVesselCount
import tqdm


class AbstractPreprocessor:
    def __init__(self, simulation:Simulation, output_parent_folder='visualisations', name='info'):
        self.sim = simulation
        self.analysers = []

        self.output_file = pathlib.Path(output_parent_folder, self.sim.name, self.sim.id, f'{name}.csv')
        if not os.path.exists(self.output_file.parent):
            self.output_file.parent.mkdir(exist_ok=True, parents=True)

    def _process_internal(self, start=0, stop=None, step=1):
        data = pd.DataFrame(columns=['timestep'] + [a.name for a in self.analysers], dtype=int).set_index('timestep')
        for t in tqdm.tqdm(self.sim.results_timesteps[start:stop:step]):
            tp = self.sim.read_timepoint(t)
            row = [0 for _ in range(len(self.analysers))]
            for i, analyser in enumerate(self.analysers):
                row[i] = analyser.analyse(tp)
            data.loc[t] = row
        data.to_csv(self.output_file)

    def process(self, start=0, stop=None, step=1):
        self._process_internal(start, stop, step)

class Preprocessor(AbstractPreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analysers = [
            TumourCount(),
            TCellCount(),
            BloodVesselCount(),
        ]

    def process(self, start=0, stop=None, step=1):
        super().process(start, stop, step)

    def add_analyser(self, analyser:AbstractAnalyser):
        self.analysers.append(analyser)
