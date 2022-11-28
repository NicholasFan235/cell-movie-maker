
import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import numpy as np
import pandas as pd


class SimulationTimepoint:
    def __init__(self, results_file:str):
        self.results_file = results_file
        raw = self.read_data()
        self.n_points = raw.GetNumberOfPoints()
        self.data = pd.DataFrame(
            index=np.arange(self.n_points),
            columns=["x", "y", "z", "volume", "potency", "damage", "oxygen", "il10"])
        self.load_locations(raw)
        self.load_data(raw.PointData)

    def read_data(self):
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(self.results_file)
        reader.Update()
        return dsa.WrapDataObject(reader.GetOutput())
    
    def load_locations(self, raw):
        self.data.loc[:,["x", "y", "z"]] = raw.Points

    def load_data(self, raw):
        self.load_volume(raw)
        self.load_potency(raw)
        self.load_damage(raw)
        self.load_oxygen(raw)
        self.load_il10(raw)
        self.load_damage(raw)
        self.load_potency(raw)
    
    def load_volume(self, raw):
        self.load_value(raw, "volume")
    
    def load_potency(self, raw):
        self.load_value(raw, "potency")
    
    def load_damage(self, raw):
        self.load_value(raw, "damage")
    
    def load_oxygen(self, raw):
        self.load_value(raw, "oxygen")
    
    def load_il10(self, raw):
        self.load_value(raw, "il10")
    
    def load_value(self, raw, name):
        self.data[name] = raw[name]
