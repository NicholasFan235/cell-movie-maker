import sys
import os
import cell_movie_maker as cmm

import warnings
warnings.filterwarnings('ignore')

assert len(sys.argv)==3, f"Bad Parameters, <simulaton-directory> <version>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."



simulation = cmm.Simulation(results_folder)

version = int(sys.argv[2])
if version == 1:
    visualiser = cmm.TCellABMPressureVisualiser(simulation, visualisation_name='tcellabm-pressure')
elif version == 2:
    visualiser = cmm.TCellABMPressureVisualiser2(simulation, visualisation_name='tcellabm-pressure2')
visualiser.visualise(auto_execute=False)
visualiser.figsize=(8,6)
visualiser.sim.for_timepoint(visualiser.visualise_frame, step=1)

