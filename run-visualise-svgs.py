import sys
import os
import cell_movie_maker as cmm

assert len(sys.argv)>=2, f"Missing simulation folder. Usage: {sys.argv[0]} <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."

tumour_necrotic_concentration = 0
if len(sys.argv)>2: tumour_necrotic_concentration = float(sys.argv[2])

simulation = cmm.Simulation(results_folder)
visualiser = cmm.svg.SVGVisualiser(simulation)
visualiser.visualise(step=1, maxproc=8,
                     #example-tcellabm-simulation 5
                     tumour_necrotic_concentration=0.01,tumour_hypoxic_concentration=0.04,
                     stroma_hypoxic_concentration=.1, stroma_necrotic_concentration=.05,
                     #dynamic-vessels-tumour-simulation 2
                     #tumour_necrotic_concentration=0.2,tumour_hypoxic_concentration=0.3,
                     #stroma_hypoxic_concentration=0.4,stroma_necrotic_concentration=0.2,
                     p_max=5)

