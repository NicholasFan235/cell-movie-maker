from .svg_stitcher import SVGStitcher
from ..plotters.legacy_plotters.tda_plotter import RipsFiltrationPlotter


class SVGStitcherRipser(SVGStitcher):
    def __init__(self, simulation, visualisation_name='rips-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AB;AC", n)
        
        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        RipsFiltrationPlotter.plot_damaged_tumour_rips(fig, axs['B'], simulation_timepoint)
        RipsFiltrationPlotter.plot_healthy_tumour_rips(fig, axs['C'], simulation_timepoint)
        
        return self.post(fig, axs, n)

