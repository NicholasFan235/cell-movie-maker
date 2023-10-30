import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''
    https://stackoverflow.com/a/18926541
    '''
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

def sub_cmap(cmap, vmin, vmax):
    return lambda v: cmap(vmin + (vmax - vmin) * v)

class SVGWriter:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.name = "tcell-svg"
        self.background = 'ecm'
        self.background_max = None
    
    def plot_ecm(self, simulation_timepoint):
        os = '<g stroke-width="0.1">'
        density = simulation_timepoint.ecm_density_data
        for i in range(density.shape[0]):
            for j in range(density.shape[1]):
                x = 255-int(density[i][j]*255)
                if (self.background_max != None):
                    x = min(self.background_max, x)
                f = f'rgb({x},{x},{x})'
                os += f'<rect x="{j-.5}" y="{i-.5}" fill="{f}" width="1" height="1" stroke="{f}"/>'
        return os + '</g>\n'

    def plot_oxygen(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap = mpl.colormaps['cividis']
        os = '<g stroke-width="0.1">'
        ox = simulation_timepoint.oxygen_data
        for i in range(ox.shape[0]):
            for j in range(ox.shape[1]):
                colour = cmap(norm(ox[i][j]))
                f = f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
                os += f'<rect x="{j-.5}" y="{i-.5}" fill="{f}" width="1" height="1" stroke="{f}"/>'
        return os + '</g>\n'
    
    def plot_ccl5(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=50)
        cmap = mpl.colormaps['magma']
        os = '<g stroke-width="0.1">'
        ccl5 = simulation_timepoint.ccl5_data
        for i in range(ccl5.shape[0]):
            for j in range(ccl5.shape[1]):
                colour = cmap(norm(ccl5[i][j]))
                f = f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
                os += f'<rect x="{j-.5}" y="{i-.5}" fill="{f}" width="1" height="1" stroke="{f}"/>'
        return os + '</g>\n'
    
    def plot_stroma(self, simulation_timepoint):
        os = '<g fill="lightblue" opacity=".5" stroke-width="0">'
        for _,c in simulation_timepoint.stroma_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + "</g>\n"

    def plot_tumour(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0.1, vmax=0.9)
        cmap = truncate_colormap('Purples_r', 0.2, 0.9)
        os = '<g stroke-width=".1" stroke="black">'
        for _,c in simulation_timepoint.tumour_data.iterrows():
            colour = cmap(norm(c.damage))
            f=f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

    def plot_cytotoxic(self, simulation_timepoint):
        os = '<g stroke-width=".1" stroke="darkorange" fill="darkorange">'
        for _, c in simulation_timepoint.cytotoxic_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" opacity="{max(0.1, c.potency)}"/>'
        return os + '</g>\n'

    def plot_macrophages(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue" opacity=".5">'
        for _, c in simulation_timepoint.macrophages_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'
        
    def plot_blood_vessels(self, simulation_timepoint):
        os = '<g fill="red" stroke-width="0">'
        for _,c in simulation_timepoint.blood_vessel_data.iterrows():
            os += f'<circle cx="{c.x:.5f}" cy="{c.y:.5f}" r="{c.radius:.5f}"/>'
        return os + '</g>\n'

    def plot_background(self, simulation_timepoint):
        if self.background == 'ecm': return self.plot_ecm(simulation_timepoint)
        elif self.background == 'oxygen': return self.plot_oxygen(simulation_timepoint)
        elif self.background == 'ccl5': return self.plot_ccl5(simulation_timepoint)
        return '<rect width="100%" height="100%" fill="white"/>\n'

    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">\n'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_stroma(simulation_timepoint)
        os += self.plot_macrophages(simulation_timepoint)
        os += self.plot_blood_vessels(simulation_timepoint)
        os += self.plot_tumour(simulation_timepoint)
        os += self.plot_cytotoxic(simulation_timepoint)
        return os + '</svg>\n'

class TumourSVGWriter(SVGWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "tumour-svg"
        self.background = 'ecm'

    def plot_stroma(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue" opacity=".5">'
        for _, c in simulation_timepoint.stroma_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'

    def plot_macrophages(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue" opacity=".5">'
        for _, c in simulation_timepoint.macrophages_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'

    def plot_tumour(self, simulation_timepoint):
        os = '<g stroke-width=".1" stroke="black" fill="purple">'
        for _, c in simulation_timepoint.tumour_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'

class HypoxiaSVGWriter(SVGWriter):
    def __init__(self, tumour_necrotic_concentration=0, tumour_hypoxic_concentration=0,
                 stroma_necrotic_concentration=0, stroma_hypoxic_concentration=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_params_if_exists = True
        if self.use_params_if_exists and sim is not None and sim.parameters is not None:
            if 'TumourHypoxicConcentration' in sim.parameters:
                tumour_hypoxic_concentration = sim.parameters['TumourHypoxicConcentration']
            if 'TumourNecroticConcentration' in sim.parameters:
                tumour_necrotic_concentration = sim.parameters['TumourNecroticConcentration']
            if 'StromaHypoxicConcentration' in sim.parameters:
                stroma_hypoxic_concentration = sim.parameters['StromaHypoxicConcentration']
            if 'StromaNecroticConcentration' in sim.parameters:
                stroma_necrotic_concentration = sim.parameters['StromaNecroticConcentration']
        self.tumour_necrotic_concentration = tumour_necrotic_concentration
        self.tumour_hypoxic_concentratior = max(tumour_hypoxic_concentration, tumour_necrotic_concentration)
        self.stroma_necrotic_concentration = stroma_necrotic_concentration
        self.stroma_hypoxic_concentration = max(stroma_hypoxic_concentration, stroma_necrotic_concentration)
        self.name = "hypoxia-svg"
        self.background = 'ecm'

    def plot_stroma(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue">'
        for _, c in simulation_timepoint.stroma_data.iterrows():
            o = 1
            if c.oxygen < self.stroma_necrotic_concentration: o = .2
            elif c.oxygen < self.stroma_hypoxic_concentration: o = .8
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" opacity="{o}"/>'
        return os + '</g>\n'

    def plot_macrophages(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue">'
        for _, c in simulation_timepoint.macrophages_data.iterrows():
            o = 1
            if c.oxygen < self.stroma_necrotic_concentration: o = .2
            elif c.oxygen < self.stroma_hypoxic_concentration: o = .8
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" opacity="{o}"/>'
        return os + '</g>\n'

    def plot_tumour(self, simulation_timepoint):
        os = '<g stroke-width=".1" stroke="black">'
        for _, c in simulation_timepoint.tumour_data.iterrows():
            f = "purple"
            if c.oxygen < self.tumour_necrotic_concentration: f = "white"
            elif c.oxygen < self.tumour_hypoxic_concentratior: f = "mediumpurple"
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

class PressureSVGWriter(SVGWriter):
    def __init__(self, p_max=10, **kwargs):
        super().__init__(**kwargs)
        self.p_max = p_max
        self.name = "pressure-svg"
        self.background = 'ecm'
        
    def plot_cells(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=self.p_max)
        cmap = mpl.colormaps['cividis']
        os = '<g stroke-width="0" opacity=".8">'
        for _, c in simulation_timepoint.data.iterrows():
            colour = cmap(norm(c.pressure))
            f=f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_cells(simulation_timepoint)
        return os + '</svg>\n'


class DensitySVGWriter(SVGWriter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "density-svg"
        self.background = 'ecm'
        
    def plot_cells(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap = mpl.colormaps['Wistia']
        os = '<g stroke-width="0" opacity=".8">'
        for _, c in simulation_timepoint.data.iterrows():
            colour = cmap(norm(c.density))
            f=f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_cells(simulation_timepoint)
        return os + '</svg>\n'

class OxygenSVGWriter(SVGWriter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "oxygen-svg"
        self.background = None
        
    def plot_cells(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        cmap = mpl.colormaps['inferno']
        os = '<g stroke-width="0" opacity=".8">'
        for _, c in simulation_timepoint.data.iterrows():
            colour = cmap(norm(c.oxygen))
            f=f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_cells(simulation_timepoint)
        return os + '</svg>\n'

class CCL5SVGWriter(SVGWriter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ccl5-svg"
        self.background = 'ecm'
        self.background_max = 192
        
    def plot_ccl5(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0, vmax=50)
        cmap = mpl.colormaps['magma']
        ccl5 = simulation_timepoint.ccl5_data
        os = '<g><g stroke-width="0">'
        rotations = -90+np.arctan2(*np.gradient(ccl5)) * 180/np.pi
        for i in range(ccl5.shape[0]):
            for j in range(ccl5.shape[1]):
                colour = cmap(norm(ccl5[i][j]))
                r=min(0.4, max(0.2,norm(ccl5[i][j])))*2
                f = f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
                os += f'<polygon points=".05,0 .05,.25 .2,.25 0,.5 -.2,.25 -.05,.25 -.05,0" fill="{f}" transform="translate({j} {i})scale({r})rotate({int(rotations[i][j])})"/>'
        os += '</g>\n<g stroke-width="0.1">'
        for i in range(ccl5.shape[0]):
            for j in range(ccl5.shape[1]):
                colour = cmap(norm(ccl5[i][j]))
                f = f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
                r=min(0.4, max(0.2,norm(ccl5[i][j])))/2
                os += f'<circle cx="{j}" cy="{i}" fill="{f}" r="{r}" stroke="{f}"/>'
        return os + '</g></g>\n'

    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_ccl5(simulation_timepoint)
        return os + '</svg>\n'



class MacrophageSVGWriter(SVGWriter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "macrophage-svg"
        self.background = None

    def plot_stroma(self, simulation_timepoint):
        os = '<g stroke-width="0" fill="lightblue" opacity=".5">'
        for _, c in simulation_timepoint.stroma_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'

    def plot_macrophages(self, simulation_timepoint):
        norm = mpl.colors.Normalize(vmin=0.0, vmax=1)
        cmap = truncate_colormap('summer_r', 0.0, 1.0)
        os = '<g stroke-width="0" stroke="black">'
        for _,c in simulation_timepoint.macrophages_data.iterrows():
            colour = cmap(norm(c.phenotype))
            f=f'rgb({int(255*colour[0])},{int(255*colour[1])},{int(255*colour[2])})'
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}" fill="{f}"/>'
        return os + '</g>\n'

    def plot_tumour(self, simulation_timepoint):
        os = '<g stroke-width="0" stroke="lightpink" fill="lightpink">'
        for _, c in simulation_timepoint.tumour_data.iterrows():
            os += f'<circle cx="{c.x:.4f}" cy="{c.y:.4f}" r="{c.radius:.3f}"/>'
        return os + '</g>\n'
    
    def to_svg(self, simulation_timepoint):
        os = f'<svg width="{self.width}" height="{self.height}">\n'
        os += self.plot_background(simulation_timepoint)
        os += self.plot_stroma(simulation_timepoint)
        os += self.plot_macrophages(simulation_timepoint)
        os += self.plot_blood_vessels(simulation_timepoint)
        os += self.plot_tumour(simulation_timepoint)
        return os + '</svg>\n'
