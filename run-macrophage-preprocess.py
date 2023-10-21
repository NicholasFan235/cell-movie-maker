import sys
import os
import cell_movie_maker as cmm

assert len(sys.argv)==2, f"Missing simulation folder. Usage: {sys.argv[0]} <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
simulation_folder = os.path.abspath(sys.argv[1])
assert os.path.exists(simulation_folder), f"Folder not found: {simulation_folder}."

results_folder = os.path.join(simulation_folder, 'results_from_time_0')
assert os.path.exists(results_folder), f"Folder not found: {results_folder}."

simulation = cmm.MacrophageSimulation(results_folder)

preprocessor = cmm.Preprocessor(simulation, output_parent_folder='macrophage-visualisations')
preprocessor.analysers = []

preprocessor.add_analyser(cmm.preprocessor.TumourCount())
preprocessor.add_analyser(cmm.preprocessor.MacrophageCount())
for p in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
    preprocessor.add_analyser(cmm.preprocessor.MacrophagePhenotypeCount(phenotype_percent=int(p)))


preprocessor.process()
