from .simulation import Simulation

import functools
import pandas as pd
import os
import pathlib


class Simulation1D(Simulation):
    def __init__(self, results_folder:str):
        self.results_folder = pathlib.Path(results_folder) # Path to results_from_time_0
        assert self.results_folder.is_dir(), f'{self.results_folder} does not exist, or is a file.'

        self.id = os.path.basename(os.path.dirname(self.results_folder))
        self.name = os.path.basename(os.path.dirname(os.path.dirname(self.results_folder)))
        
        self.read_parameters()
        self.load_data()

    def load_data(self):
        with open(pathlib.Path(self.results_folder, 'results.viznodes'), 'r') as f:
            self.position_data = pd.DataFrame.from_dict({float(l.split('\t')[0].strip()): [float(x) for x in l.split('\t')[1].strip().split(' ')] for l in f.readlines()}, orient='index')
    
        pressure_file = pathlib.Path(self.results_folder, 'celldata_pressure.dat')
        if pressure_file.exists():
            with open(pressure_file, 'r') as f:
                self.pressure_data = pd.DataFrame.from_dict({float(l.split('\t')[0].strip()): [float(x) for x in l.split('\t')[1].strip().split(' ')] for l in f.readlines()}, orient='index')
        else:
            self.pressure_data = None

    @property
    def timepoints(self)->list[float]:
        return self.position_data.index.to_list()
    
    def read_timepoint(self, timepoint:float)->pd.DataFrame:
        return pd.DataFrame({
            'x':self.position_data.loc[timepoint, :],
            'pressure':self.pressure_data.loc[timepoint,:],
            })
    

