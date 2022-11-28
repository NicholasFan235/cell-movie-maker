import cell_movie_maker as cmm

simulation_folder = "/home/linc4121/Chaste/testoutput/TCellABM/test/sim_1"

visualiser = cmm.SimulationVisualiser(simulation_folder)
visualiser.visualise(step=1)

