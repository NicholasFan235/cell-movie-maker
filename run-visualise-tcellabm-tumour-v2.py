import sys
import os
import cell_movie_maker as cmm

import warnings
warnings.filterwarnings('ignore')

assert len(sys.argv)==2, f"Bad Parameters, <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."



simulation = cmm.Simulation(results_folder)

visualiser = cmm.TCellABMTumourVisualiserV2(simulation, visualisation_name='tcellabm-tumour')
visualiser.visualise(step=1, maxproc=1, clean_dir=False)

