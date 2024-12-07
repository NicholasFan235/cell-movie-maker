from .svg_stitcher import SVGStitcher
from .svg_stitcher_macrophages import MacrophageSVGStitcher
import muspan as ms
from ..plotters.legacy_plotters.muspan_plotter import MuspanPCFPlotter, MuspanMacrophagePCFPlotter
from ..plotters.legacy_plotters.graph_stats_plotter import GraphAssociationsPlotter
from ..plotters.legacy_plotters.tda_plotter import RipsFiltrationPlotter

class CustomStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name, output_parent_folder='visualisations'):
        super().__init__(simulation, output_parent_folder=output_parent_folder, visualisation_name=visualisation_name)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def read_pointcloud(self, simulation_timepoint, damage=True, potency=True):
        pc = ms.pointcloud.generatePointCloud('Test',simulation_timepoint.data[['x', 'y']].to_numpy())
        pc.addLabels('Celltype', 'categorical', simulation_timepoint.data.cell_type.to_numpy())
        if potency: pc.addLabels('potency', 'continuous', simulation_timepoint.data.potency.to_numpy())
        if damage: pc.addLabels('damage', 'continuous', simulation_timepoint.data.damage.to_numpy())
        return pc

    def process_frame(self, n):
        raise NotImplementedError
    

class CustomStitcherMacrophages(MacrophageSVGStitcher):
    def __init__(self, simulation, visualisation_name, output_parent_folder='macrophage-visualisations'):
        super().__init__(simulation, output_parent_folder=output_parent_folder, visualisation_name=visualisation_name)
        self.probe_vis_type = 'macrophage-svg-png'

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        raise NotImplementedError