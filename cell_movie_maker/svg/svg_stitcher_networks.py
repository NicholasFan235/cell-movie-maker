from .svg_stitcher import SVGStitcher
#from ..graph_stats_plotter import GraphAssociationsPlotter


class SVGStitcherGraphStats(SVGStitcher):
    def __init__(self, simulation, visualisation_name='graph-stats-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
    
    def run(self, *args, **kwargs):
        #self.graph_stats_plotter = GraphAssociationsPlotter()
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AAB;AAC", n)
        
        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.graph_stats_plotter.plot_associations(fig, axs['B'], simulation_timepoint)
        self.graph_stats_plotter.plot_morans_index_coefficients(fig, axs['C'], simulation_timepoint)
        
        return self.post(fig, axs, n)

