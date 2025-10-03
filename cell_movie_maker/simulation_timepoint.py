
import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
import pandas as pd
import pathlib
import xml.etree.ElementTree

class Simulation:
    pass

class SimulationTimepoint:
    def __init__(self, id, name, results_folder:pathlib.Path, timestep:int, sim:Simulation):
        self.id = id # e.g. sim_0
        self.name = name # experiment name
        self.results_folder = pathlib.Path(results_folder)
        self.results_file = self.results_folder.joinpath('results_{}.vtu'.format(timestep))
        self.timestep = timestep
        self.sim = sim
        self.ok = False
        raw = self.read_data()
        self.n_points = raw.GetNumberOfPoints()
        self.data = pd.DataFrame(
            index=np.arange(self.n_points))
        self.columns = set()
        self.load_locations(raw)
        self.load_data(raw.PointData)

    def read_data(self):
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(str(self.results_file))
        self.ok = reader.CanReadFile(str(self.results_file))
        if self.ok: reader.Update()
        return dsa.WrapDataObject(reader.GetOutput())
    
    def load_locations(self, raw):
        self.data.loc[:,["x", "y", "z"]] = raw.Points
        self.columns = set()

    def load_data(self, raw):
        self.load_value(raw, 'volume')
        self.data['radius'] = np.sqrt(self.data.volume/np.pi)
        self.load_value(raw, 'Ages')
        self.load_value(raw, "potency")
        self.load_value(raw, "damage", 0)
        self.load_value(raw, "oxygen")
        self.load_value(raw, "ccl5")
        self.load_value(raw, "cxcl9")
        self.load_value(raw, "ifn-gamma")
        self.load_value(raw, "density")
        self.load_value(raw, "cell_type")
        self.load_value(raw, "damping_coefficient")
        self.load_value(raw, "friction")
        self.load_value(raw, "pressure")
        self.load_value(raw, "target_radius")

        def interpret_cell_type(cell_type):
            if cell_type == 0: return 'Stroma'
            elif cell_type == 1: return 'Tumour'
            elif cell_type == 2: return 'T Cell'
            elif cell_type == 3: return 'Macrophage'
            elif cell_type == 4: return 'Blood Vessel'
            else: return 'Unknown'
        def potency_map(potency):
            if potency >= 0: return 'T Cell'
            elif potency == -1: return 'Stroma'
            elif potency == -2: return 'Tumour'
            elif potency == -3: return 'Macrophage'
            elif potency == -4: return 'Blood Vessel'
            else: return 'Unknown'
        self.data['cell_type'] = list(map(interpret_cell_type, self.data.cell_type))
        #self.data['cell_type'] = list(map(potency_map, self.data.potency))
        self.data.loc[self.data.potency < 0, 'potency'] = np.nan
        self.data.loc[self.data.damage < 0, 'damage'] = np.nan

        self.data['tissue_stress'] = 1 - self.data['radius']/self.data['target_radius']
        self.data.loc[~np.isfinite(self.data.tissue_stress), 'tissue_stress'] = -1

        if self.sim.parameters and 'potency' in self.data and 'CD8InitialPotency' in self.sim.parameters:
            self.data['exhaustion %'] = 1-self.data['potency']/self.sim.parameters['CD8InitialPotency']

    
    def load_value(self, raw, name, default=np.nan, new_key=None):
        if new_key is None: new_key = name
        if name in raw.keys():
            self.data[new_key] = raw[name]
        else:
            self.data[new_key] = default
        self.columns.add(new_key)

    @property
    def cytotoxic_data(self):
        return self.data.loc[self.data.cell_type == 'T Cell']
    
    @property
    def stroma_data(self):
        return self.data.loc[self.data.cell_type == 'Stroma']

    @property
    def tumour_data(self):
        return self.data.loc[self.data.cell_type == 'Tumour']
    
    @property
    def macrophages_data(self):
        return self.data.loc[self.data.cell_type == 'Macrophage']
    
    @property
    def macrophage_data(self):
        return self.data.loc[self.data.cell_type == 'Macrophage']
    
    @property
    def blood_vessel_data(self):
        return self.data.loc[self.data.cell_type == 'Blood Vessel']

    @property
    def ccl5_data(self):
        return self.read_pde('tcellpdes', 'ccl5')

    @property
    def cxcl9_data(self):
        return self.read_pde('tcellpdes', 'cxcl9')

    @property
    def ifng_data(self):
        return self.read_pde('tcellpdes', 'ifn-gamma')

    @property
    def ecm_density_data(self):
        return self.read_pde('tcellpdes', 'density')

    @property
    def oxygen_data(self):
        return self.read_pde('oxygen')

    def read_pde(self, file, chemokine=None):
        if (chemokine is None): chemokine = file
        p = pathlib.Path(self.results_folder, f"pde_results_{file}_{self.timestep}.vtu")
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(str(p))
        reader.Update()
        output = dsa.WrapDataObject(reader.GetOutput())
        shape = output.Points.max(axis=0)
        shape = (int(np.sqrt(output.Points.shape[0])), int(np.sqrt(output.Points.shape[0])))
        #shape = (51,51)
        return output.PointData[chemokine].reshape(shape)
    
    def to_muspan(self):
        import muspan as ms
        domain = ms.domain(f'{self.name} {self.id} {self.timestep}')
        domain.add_points(self.data[['x', 'y']].to_numpy())
        for c in self.data.columns:
            domain.add_labels(c, self.data[c])
        return domain
    
    def append_analysis(self, analyser):
        df = analyser.analyse(self, self.sim).set_index('cell_id')
        self.data = self.data.drop(df.columns, axis=1, errors='ignore').join(df, on='cell_id', how='left')


class MacrophageSimulationTimepoint(SimulationTimepoint):
    def __init__(self, id, name, results_folder:pathlib.Path, timestep:int, sim:Simulation):
        super().__init__(id, name ,results_folder, timestep, sim)

    def load_data(self, raw):
        self.load_value(raw, 'csf1')
        self.load_value(raw, 'csf1_grad_x')
        self.load_value(raw, 'csf1_grad_y')
        self.load_value(raw, 'cxcl12')
        self.load_value(raw, 'cxcl12_grad_x')
        self.load_value(raw, 'cxcl12_grad_y')
        self.load_value(raw, 'egf')
        self.load_value(raw, 'egf_grad_x')
        self.load_value(raw, 'egf_grad_y')
        self.load_value(raw, 'oxygen')
        self.load_value(raw, 'phenotype')
        self.load_value(raw, 'tgf')
        self.load_value(raw, 'tgf_grad_x')
        self.load_value(raw, 'tgf_grad_y')
        self.load_value(raw, 'volume')
        self.load_value(raw, 'target_radius')
        self.load_value(raw, 'pressure')
        self.data['radius'] = np.sqrt(self.data.volume / np.pi)

        self.load_value(raw, "cell_type", new_key="cell_type_raw")
        self.load_value(raw, "cell_type")
        def interpret_cell_type(cell_type):
            if cell_type == 0: return 'Stroma'
            elif cell_type == 1: return 'Tumour'
            elif cell_type == 4: return 'Blood Vessel'
            elif cell_type == 7: return 'Macrophage'
            elif cell_type == 3: return 'Macrophage'
            else: return 'Unknown'
        self.data['cell_type'] = list(map(interpret_cell_type, self.data.cell_type))

    @property
    def cxcl12_data(self):
        return self.read_pde('cxcl12')
    
    @property
    def csf1_data(self):
        return self.read_pde('csf1')
    
    @property
    def egf_data(self):
        return self.read_pde('egf')
    
    @property
    def tgf_data(self):
        return self.read_pde('tgf')
    
    def read_vessels(self):
        p = pathlib.Path(self.results_folder, f"results.parameters")
        tree = xml.etree.ElementTree.parse(p)
        raw = tree.find('SimulationModifiers/EllipticBoxDomainPdeModifier_VariableTimestep_PointVesselBCs-2/mVesselLocations')
        assert raw is not None, f"Could not find vessel locations in {p}"
        vesselLocations = [[float(x) for x in p.strip('[], \t').split(',')] for p in raw.text.strip(' ,\t').split('],[')]
        for xy in vesselLocations: self.data.loc[len(self.data), ['x', 'y', 'cell_type', 'oxygen', 'radius']] =\
            [xy[0], xy[1], 'Blood Vessel', 1, .5]



class LiverMetSimulationTimepoint(SimulationTimepoint):
    def __init__(self, id, name, results_folder:pathlib.Path, timestep:int, sim:Simulation):
        super().__init__(id, name ,results_folder, timestep, sim)

    def load_data(self, raw):
        self.load_value(raw, 'oxygen')
        self.load_value(raw, 'CXCL8')
        self.load_value(raw, 'volume')
        self.data['radius'] = .5#np.sqrt(self.data.volume / np.pi)

        self.load_value(raw, 'Legacy Cell types', new_key='cell_type')
        def interpret_cell_type(cell_type):
            match cell_type:
                case 10: return 'T-Cell'
                case 11: return 'Background'
                case 12: return 'Met'
                case 13: return 'Neutrophil'
                case 14: return 'Fibroblast'
                case _: return 'Unknown'
        self.data['cell_type'] = list(map(interpret_cell_type, self.data.cell_type))

    @property
    def tcell_data(self):
        return self.data.loc[self.data.cell_type == 'T-Cell']
        
    @property
    def background_data(self):
        return self.data.loc[self.data.cell_type == 'Background']

    @property
    def met_data(self):
        return self.data.loc[self.data.cell_type == 'Met']

    @property
    def neutrophil_data(self):
        return self.data.loc[self.data.cell_type == 'Neutrophil']

    @property
    def fibroblast_data(self):
        return self.data.loc[self.data.cell_type == 'Fibroblast']


