import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import sys
sys.path.append('/home/linc4121/Code/projects/MuSpAn')
import MuSpAn as ms


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

class MuspanPCFPlotter:
    def __init__(self, pcf_kwargs={}):
        self.pcf_kwargs = {
            'maxR': 50,
            'annulusStep': 0.625,
            'annulusWidth': 0.625
        }
        self.pcf_kwargs.update(pcf_kwargs)
    
    def plot_tcell_tcell_pcf(self, fig, ax, pc):
        categories = pc.labels['Celltype']['categories']
        ax.set_title('T Cell - T Cell')
        if not 'T Cell' in categories:
            return

        radii, g, contributions = ms.statistics.pairCorrelationFunction(
            pc,'Celltype',['T Cell','Tumour'], **self.pcf_kwargs)
        fig, ax = ms.statistics.plotPCF(
            pc, radii, g, contributions, 'Celltype',['T Cell','T Cell'],
            quadratSize=None, ax=ax)
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    def plot_tcell_tumour_pcf(self, fig, ax, pc):
        categories = pc.labels['Celltype']['categories']
        ax.set_title('T Cell - Tumour')
        if not ('T Cell' in categories and 'Tumour' in categories):
            return

        radii, g, contributions = ms.statistics.pairCorrelationFunction(
            pc,'Celltype',['T Cell','Tumour'], **self.pcf_kwargs)
        fig, ax = ms.statistics.plotPCF(
            pc, radii, g, contributions, 'Celltype',['T Cell','Tumour'],
            quadratSize=None, ax=ax)
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    def plot_tumour_tumour_pcf(self, fig, ax, pc):
        categories = pc.labels['Celltype']['categories']
        ax.set_title('Tumour - Tumour')
        if not 'Tumour' in categories:
            return

        radii, g, contributions = ms.statistics.pairCorrelationFunction(
            pc,'Celltype',['Tumour','Tumour'], **self.pcf_kwargs)
        fig, ax = ms.statistics.plotPCF(
            pc, radii, g, contributions, 'Celltype',['Tumour','Tumour'],
            quadratSize=None, ax=ax)
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

class MuspanWeightedPCFPlotter:
    def __init__(self, pcf_kwargs={}):
        self.pcf_kwargs = {
            'maxR': 50,
            'annulusStep': 0.625,
            'annulusWidth': 0.625
        }
        self.pcf_kwargs.update(pcf_kwargs)
    
    def plot_potency_tumour_pcf(self, fig, ax, pc):
        ax.set_title('Tumour - T Cell Potency wPCF')
        categories = pc.labels['Celltype']['categories']
        if not ('T Cell' in categories and 'Tumour' in categories):
            return

        PCF_radii_lower, targetP, wPCF = ms.statistics.weightedPairCorrelationFunction(
            pc,'Celltype','Tumour','potency', **self.pcf_kwargs)
        fig, ax = ms.statistics.plotWeightedPCF(PCF_radii_lower, targetP, wPCF, ax=ax)
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    
    def plot_damage_tcell_pcf(self, fig, ax, pc):
        ax.set_title('T Cell - Tumour Damage wPCF')
        categories = pc.labels['Celltype']['categories']
        if not ('T Cell' in categories and 'Tumour' in categories):
            return

        PCF_radii_lower, targetP, wPCF = ms.statistics.weightedPairCorrelationFunction(
            pc,'Celltype','T Cell','damage', **self.pcf_kwargs)
        fig, ax = ms.statistics.plotWeightedPCF(PCF_radii_lower, targetP, wPCF, ax=ax)
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

