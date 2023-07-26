from ..simulation_timepoint import SimulationTimepoint


class AbstractAnalyser:
    def __init__(self, name='abstract', dtype=float):
        self.name = name
        self.dtype = dtype

    def analyse(self, tp:SimulationTimepoint):
        raise NotImplementedError

