from ._abstract_multisim_stitcher import AbstractMultisimStitcher
import matplotlib.pylab as plt
import os


class MultisimStitcherMacrophages(AbstractMultisimStitcher):
    def __init__(self, simulations, output_parent_folder='visualisations', visualisation_name='multisim-stitch-macrophages', n_rows=1):
        super().__init__(simulations, output_parent_folder, visualisation_name, n_rows)

        self.probe_vis_type = 'macrophage-svg-png'

    def plot_simulation(self, fig, axs, sim, n):
        axs.imshow(self.get_frame(sim, 'macrophage-svg-png', n))
        axs.set_xticks([])
        axs.set_yticks([])
        axs.set_title(f'{sim.name}/{sim.id} #{n}', fontsize=30)

