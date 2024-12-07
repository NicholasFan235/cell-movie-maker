from ..simulation_visualiser import AbstractSimulationVisualiser
from ..simulation import Simulation
from ..simulation_timepoint import SimulationTimepoint
from .svg_writer import SVGWriter, TumourSVGWriter, HypoxiaSVGWriter, PressureSVGWriter, OxygenSVGWriter, CCL5SVGWriter, DensitySVGWriter
import os
import shutil
import pathlib
import logging

class SVGVisualiser(AbstractSimulationVisualiser):
    def __init__(self, visualisation_name='svg', width=100, height=100, **kwargs):
        super().__init__(visualisation_name=visualisation_name, **kwargs)
        self.writers = [
            SVGWriter(width, height),
            TumourSVGWriter(width=width, height=height),
            HypoxiaSVGWriter(width=width, height=height),
            PressureSVGWriter(width=width, height=height, p_max=10),
            OxygenSVGWriter(width=width, height=height),
            CCL5SVGWriter(width=width, height=height),
            DensitySVGWriter(width=width, height=height),
        ]

    def visualise_frame(self, sim:Simulation, tp:SimulationTimepoint, frame_num:int):
        for w in self.writers:
            svg = w.to_svg(tp, sim)
            p = pathlib.Path(self.output_folder, w.name)
            if not p.exists():
                p.mkdir(exist_ok=True)
            with open(pathlib.Path(p, f'frame_{frame_num}.svg'), 'w') as f:
                f.write(svg)

    def visualise(self, sim, auto_execute=True, maxproc=64, start=0, stop=None, step=1, clean_dir=True,
                  disable_tqdm=False, offset=0):
        if auto_execute:
            for w in self.writers:
                if os.path.exists(self.output_folder.joinpath(sim.name, sim.id, w.name)) and clean_dir:
                    shutil.rmtree(self.output_folder.joinpath(sim.name, sim.id, w.name))
                pathlib.Path(os.path.join(self.output_folder, w.name)).mkdir(exist_ok=True,parents=True)
        
        self.start = start
        self.stop = stop
        self.step = step

        if auto_execute:
            sim.for_timepoint(self.visualise_frame, start=self.start, stop=self.stop, step=self.step, maxproc=maxproc, disable_tqdm=disable_tqdm, offset=offset)


