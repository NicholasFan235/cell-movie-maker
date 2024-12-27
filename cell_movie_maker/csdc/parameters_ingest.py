import chaste_simulation_database_connector as csdc
from ..experiment import Experiment
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
import typing
import tqdm


def chunk(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]

class ParametersIngest:
    def __init__(self, db:csdc.Connection):
        self.db:csdc.Connection = db

    def ingest_experiment(self, experiment:typing.Type[Experiment], disable_tqdm:bool=False):
        parameters = []
        for sim_folder in tqdm.tqdm(experiment.sim_folders, disable=disable_tqdm):
            sim:Simulation = Simulation(sim_folder)
            parameters.extend([dict(
                experiment=experiment.name, iteration=int(sim.iteration),
                parameter_name=k, parameter_value=v, was_varied=False)
                for k,v in sim.parameters.items()])
        self.db.add_bulk_parameters(parameters, commit=True, close_connection=True)
        self.db.interpret_varied_parameters(experiment)
        self.db.commit()
        self.db.close_connection()
    
    def ingest_simulation(self, simulation:typing.Type[Simulation], varied_params:set|list=None):
        raise NotImplementedError
