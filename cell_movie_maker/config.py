import os
import sys
import pathlib


def env_var(key, default=""):
    return os.environ[key] if key in os.environ else default

class Config:
    simulations_folder:pathlib.Path=pathlib.Path(env_var("CHASTE_TEST_OUTPUT"))
    output_folder:pathlib.Path=pathlib.Path(env_var('CHASTE_VISUALISATIONS_OUTPUT'))
    
