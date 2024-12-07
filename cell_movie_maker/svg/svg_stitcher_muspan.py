from .svg_stitcher import SVGStitcher
import muspan as ms
from ..plotters.legacy_plotters.muspan_plotter import MuspanPCFPlotter, MuspanWeightedPCFPlotter

class SVGStitcherMuspan(SVGStitcher):
    def __init__(self, simulation, visualisation_name='muspan-stitched', *args, **kwargs):
        super().__init__(simulation ,visualisation_name=visualisation_name, *args, **kwargs)

    def read_pointcloud(self, simulation_timepoint, damage=True, potency=True):
        pc = ms.pointcloud.generatePointCloud('Test',simulation_timepoint.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', simulation_timepoint.data.cell_type.to_numpy())
        if potency: pc.addLabels('potency', 'continuous', simulation_timepoint.data.potency.to_numpy())
        if damage: pc.addLabels('damage', 'continuous', simulation_timepoint.data.damage.to_numpy())
        return pc
    
    def plot_tumour_tumour_pcf(fig, ax, pointcloud):
        pass

class SVGStitcherPCF(SVGStitcherMuspan):
    def __init__(self, simulation, visualisation_name='pcf-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)
        pc = self.read_pointcloud(simulation_timepoint, damage=False, potency=False)

        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_tumour_damage_count(fig, axs['B'], simulation_timepoint)
        muspan_plotter_config = MuspanPCFPlotter.Config()
        MuspanPCFPlotter.plot_tumour_tumour_pcf(fig, axs['D'], pc, config=muspan_plotter_config)
        MuspanPCFPlotter.plot_tcell_tcell_pcf(fig, axs['E'], pc, config=muspan_plotter_config)
        MuspanPCFPlotter.plot_tcell_tumour_pcf(fig, axs['C'], pc, config=muspan_plotter_config)
        return self.post(fig, axs, n)
        