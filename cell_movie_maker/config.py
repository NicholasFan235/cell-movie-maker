import os
import sys
import pathlib


class Config:
    simulations_folder:pathlib.Path=pathlib.Path(os.environ["CHASTE_TEST_OUTPUT"] if "CHASTE_TEST_OUTPUT" in os.environ else "")
    output_folder:pathlib.Path=pathlib.Path('visualisations')
    
