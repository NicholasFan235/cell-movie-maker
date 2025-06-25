import os
import sys
import pathlib
import typing


def env_var(key, default=""):
    return os.environ[key] if key in os.environ else default

class Config:
    simulations_folder:pathlib.Path=pathlib.Path(env_var("CMM_SIMULATIONS_DIR"))
    output_folder:pathlib.Path=pathlib.Path(env_var('CMM_OUTPUT_DIR'))
    simulation_database=None
    def set_simulation_database(db_file:pathlib.Path):
        import chaste_simulation_database_connector as csdc
        Config.simulation_database = csdc.Connection(db_file)
    # experiment_class:cls=None
    simulation_class=None

    
