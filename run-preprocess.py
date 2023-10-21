import sys
import os
import cell_movie_maker as cmm

assert len(sys.argv)==2, f"Missing simulation folder. Usage: {sys.argv[0]} <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."

simulation = cmm.Simulation(results_folder)

preprocessor = cmm.Preprocessor(simulation)
preprocessor.add_analyser(cmm.preprocessor.HypoxicCount(
#    hypoxia_threshold=0.04)) # Standard
    hypoxia_threshold=0.2)) # test-tcellabm-pdes 3
preprocessor.add_analyser(cmm.preprocessor.NecroticCount(
#    necrosis_threshold=0.01)) # Standard
    necrosis_threshold=0.1)) # test-tcellabm-pdes 3
for p in [90, 80, 60, 20]:
    preprocessor.add_analyser(cmm.preprocessor.TCellPotencyCount(potency_percent=int(p)))
for d in [10, 20, 40, 80]:
    preprocessor.add_analyser(cmm.preprocessor.TumourDamageCount(damage_percent=int(d)))
preprocessor.process()
