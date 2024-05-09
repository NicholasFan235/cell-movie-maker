from ..simulation_visualiser import AbstractSimulationVisualiser
from .svg_writer import SVGWriter, TumourSVGWriter, HypoxiaSVGWriter, PressureSVGWriter, OxygenSVGWriter, CCL5SVGWriter, DensitySVGWriter
import os
import shutil
import pathlib

class SVGVisualiser(AbstractSimulationVisualiser):
    def __init__(self, simulation, visualisation_name='svg', **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, **kwargs)

    def visualise_frame(self, info:tuple[int,int]):
        frame_num, timepoint = info
        simulation_timepoint = self.sim.read_timepoint(timepoint)

        for w in self.writers:
            svg = w.to_svg(simulation_timepoint, self.sim)
            p = pathlib.Path(self.output_folder, w.name)
            if not p.exists():
                p.mkdir(exist_ok=True)
            with open(pathlib.Path(p, f'frame_{frame_num}.svg'), 'w') as f:
                f.write(svg)

    def visualise(self, auto_execute=True, maxproc=64, start=0, stop=None, step=1, clean_dir=True,
                  width=50, height=50,
                  tumour_hypoxic_concentration=0, tumour_necrotic_concentration=0,
                  stroma_hypoxic_concentration=0, stroma_necrotic_concentration=0,
                  p_max=10, disable_tqdm=False, writers_factory=None, offset=0):
        if not os.path.exists(self.output_folder):
            pathlib.Path(self.output_folder).mkdir(exist_ok=True)
        
        if writers_factory is None:
            self.writers = [
                SVGWriter(width, height),
                TumourSVGWriter(width=width, height=height),
                HypoxiaSVGWriter(width=width, height=height, tumour_hypoxic_concentration=tumour_hypoxic_concentration, tumour_necrotic_concentration=tumour_necrotic_concentration, stroma_hypoxic_concentration=stroma_hypoxic_concentration,stroma_necrotic_concentration=stroma_necrotic_concentration),
                PressureSVGWriter(width=width, height=height, p_max=p_max),
                OxygenSVGWriter(width=width, height=height),
                CCL5SVGWriter(width=width, height=height),
                DensitySVGWriter(width=width, height=height),
            ]
        else: self.writers = writers_factory()

        if auto_execute:
            for w in self.writers:
                if os.path.exists(os.path.join(self.output_folder, w.name)) and clean_dir:
                    shutil.rmtree(os.path.join(self.output_folder, w.name))
                pathlib.Path(os.path.join(self.output_folder, w.name)).mkdir(exist_ok=True,parents=True)
        
        self.start = start
        self.stop = stop
        self.step = step

        if auto_execute:
            self.sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc, disable_tqdm=disable_tqdm, offset=offset)


