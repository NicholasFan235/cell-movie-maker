import sys
import os
import cell_movie_maker as cmm

assert len(sys.argv)==2, f"Missing simulation folder. Usage: {sys.argv[0]} <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = sys.argv[1]

assert os.path.exists(simulation_folder), f"Folder not found: {sys.argv[1]}."

visualiser = cmm.SimulationVisualiser(simulation_folder)
visualiser.visualise_histogram(step=1)

