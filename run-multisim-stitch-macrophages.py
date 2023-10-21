import sys
import os
import cell_movie_maker as cmm
import pathlib

assert len(sys.argv)>=2, f"Missing simulation folder. Usage: {sys.argv[0]} <simulaton-directory>."


#simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"
sim_name = sys.argv[1]

sims_folder = pathlib.Path(os.environ['CHASTE_TEST_OUTPUT'], 'Macrophages', 'SimsForNic', sim_name)
assert sims_folder.exists(), f'{sims_folder} could not be found.'

n_rows = 1
if len(sys.argv) >= 3: n_rows = int(sys.argv[2])

simulations = []
for sim_id in os.listdir(sims_folder):
    simulations.append(
        cmm.MacrophageSimulation(pathlib.Path(sims_folder, sim_id, 'results_from_time_0')))

stitcher = cmm.multisim_stitchers.MultisimStitcherMacrophages(
    simulations,
    output_parent_folder='macrophage-visualisations',
    n_rows=n_rows)

stitcher.run(maxproc=4)


