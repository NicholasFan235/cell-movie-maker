import sys
import os
import cell_movie_maker as cmm

import warnings
warnings.filterwarnings('ignore')

assert len(sys.argv)==3, f"Bad Parameters, <simulaton-directory> <chemokine>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."

chemokine = sys.argv[2]


simulation = cmm.Simulation(results_folder)

visualiser = cmm.ChemokineVisualiser(simulation, visualisation_name=chemokine)
visualiser.visualise(step=1)

