
import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
import pandas as pd
import pathlib


class SimulationTimepoint:
    def __init__(self, id, name, results_folder:pathlib.Path, timestep:int):
        self.id = id
        self.name = name
        self.results_folder = results_folder
        self.results_file = pathlib.Path(self.results_folder, 'results_{}.vtu'.format(timestep))
        self.timestep = timestep
        raw = self.read_data()
        self.n_points = raw.GetNumberOfPoints()
        self.data = pd.DataFrame(
            index=np.arange(self.n_points))
        self.load_locations(raw)
        self.load_data(raw.PointData)

    def read_data(self):
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(str(self.results_file))
        reader.Update()
        return dsa.WrapDataObject(reader.GetOutput())
    
    def load_locations(self, raw):
        self.data.loc[:,["x", "y", "z"]] = raw.Points

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

    
    def load_value(self, raw, name, default=np.nan):
        if name in raw.keys():
            self.data[name] = raw[name]
        else:
            self.data[name] = default

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
        shape = (int(shape[0]+1), int(shape[1]+1))
        return output.PointData[chemokine].reshape(shape)
