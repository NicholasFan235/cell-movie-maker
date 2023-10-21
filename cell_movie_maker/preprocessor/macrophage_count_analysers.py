from ._abstract_analyser import AbstractAnalyser
from ..simulation_timepoint import MacrophageSimulationTimepoint


class MacrophageCount(AbstractAnalyser):
    def __init__(self, name='n_macrophages', dtype=int):
        super().__init__(name, dtype)

    def analyse(self, tp:MacrophageSimulationTimepoint):
        return int(tp.macrophages_data.shape[0])
    
class MacrophagePhenotypeCount(AbstractAnalyser):
    def __init__(self, name='n_macrophages_phenotype', dtype=int, phenotype_percent=0.5):
        super().__init__(name + str(phenotype_percent), dtype)
        self.threshold = phenotype_percent

    def analyse(self, tp:MacrophageSimulationTimepoint):
        return int(len(tp.macrophages_data[tp.macrophages_data.phenotype*100 <= self.threshold]))
    
