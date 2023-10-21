import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from scipy.spatial import Delaunay
from scipy.spatial.distance import cdist
from scipy.stats import linregress
import networkx as nx
import pyGraphStats
import pandas as pd


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

class GraphAssociationsPlotter:
    def __init__(self):
        pass
    
    def plot_associations(self, fig, ax, tp):
        tp.data['tmp'] = -1
        tp.data.loc[(tp.data.cell_type == 'Tumour') & (tp.data.damage <= 0.6), 'tmp'] = 0
        tp.data.loc[(tp.data.cell_type == 'Tumour') & (tp.data.damage > 0.6), 'tmp'] = 1
        tp.data.loc[(tp.data.cell_type == 'T Cell') & (tp.data.potency >= 0.5), 'tmp'] = 2
        tp.data.loc[(tp.data.cell_type == 'T Cell') & (tp.data.potency < 0.5), 'tmp'] = 3
        categories = {
            0: 'Healthy Tumour',
            1: 'Damaged Tumour',
            2: 'Healthy T-Cell',
            3: 'Exhausted T-Cell',
        }

        subset = tp.data[tp.data.tmp >= 0]
        category_counts = np.zeros((len(categories),), dtype=int)
        for i in range(len(categories)):
            category_counts[i] = np.sum(subset.tmp==i)
        R = np.diag(np.sqrt(len(subset))/category_counts)
        tri = Delaunay(subset[['x', 'y']])
        edges = [set() for i in range(len(subset))]
        distances = cdist(subset[['x', 'y']], subset[['x', 'y']])
        for a,b,c in tri.simplices:
            if distances[a,b] < 1:
                edges[a].add(b)
                edges[b].add(a)
            if distances[b,c] < 1:
                edges[b].add(c)
                edges[c].add(b)
            if distances[a,c] < 1:
                edges[a].add(c)
                edges[c].add(a)
        
        graph = pyGraphStats.Graph(len(subset), 4, subset.tmp.to_numpy(), edges)
        solver = pyGraphStats.Solver(3, [1, .5, .25])
        associations = np.array(solver.solve_from_points(graph, list(range(len(subset)))))
        associations = R@associations@R

        g = nx.Graph()
        for i, c in categories.items():
            g.add_node(i, cell_type=c)
        for i in range(associations.shape[0]):
            for j in range(i, associations.shape[1]):
                g.add_edge(i, j, weight=associations[i][j])
        
        pos = nx.circular_layout(g)
        nx.draw_networkx_nodes(g, pos, ax=ax)
        nx.draw_networkx_labels(g, pos, ax=ax, labels=categories)
        nx.draw_networkx_edges(
            g, pos, ax=ax,
            width=list(nx.get_edge_attributes(g, 'weight').values()))

    def plot_morans_index_coefficients(self, fig, ax, tp):
        data = tp.data[tp.data.cell_type.isin(['Tumour', 'T Cell'])]
        ax.set_title('Moran\'s I Coefficient for Tumour Damage')
        ax.set_ylabel('Moran\'s I Coefficient')
        ax.set_xlabel('N-Hop Neighbourhood')
        ax.set_xlim(1, 8)
        if len(data) == 0: return
        tri = Delaunay(data[['x', 'y']])

        distances = cdist(data[['x', 'y']], data[['x', 'y']])
        edges = [set() for i in range(len(data))]
        for a, b, c in tri.simplices:
            if distances[a,b] < 1:
                edges[a].add(b)
                edges[b].add(a)
            if distances[b,c] < 1:
                edges[a].add(c)
                edges[c].add(a)
            if distances[a,c] < 1:
                edges[b].add(c)
                edges[c].add(b)

        use_values = (data.cell_type=='Tumour') & (data.damage <= 1.0)
        if np.sum(use_values) == 0: return
        values = data.damage
        morans_solver = pyGraphStats.MoransSolver(len(data), edges, use_values.to_numpy(), values.to_numpy())

        morans = pd.DataFrame(columns=['N'], dtype=int).set_index('N')
        morans['Morans'] = 0.0
        morans['err'] = 0.0

        for n in range(1,9):
            soln = morans_solver.solve(n)

            mask = (np.array(soln.n_neighbours) > 0) & use_values
            mean_neighbour_values = (np.array(soln.s_neighbours) / np.array(soln.n_neighbours))[mask]
            origin_values = data.damage[mask]
            if np.sum(mask) <= 8: continue

            try:
                result = linregress(origin_values, mean_neighbour_values)
                morans.loc[n, 'Morans'] = result.slope
                morans.loc[n, 'err'] = result.stderr
            except Exception as e:
                print(e)
                continue

        ax.plot(morans.index, morans['Morans'], 'kx-')
        ax.fill_between(morans.index, morans['Morans'] + morans['err'], morans['Morans'] - morans['err'])
        
    
    def plot_morans_index_coefficients_macrophage(self, fig, ax, tp):
        data = tp.data[tp.data.cell_type.isin(['Tumour', 'Macrophage'])]
        ax.set_title('Moran\'s I Coefficient for M1-M2 Phenotype')
        ax.set_ylabel('Moran\'s I Coefficient')
        ax.set_xlabel('N-Hop Neighbourhood')
        ax.set_xlim(1, 8)
        if len(data) == 0: return
        tri = Delaunay(data[['x', 'y']])

        distances = cdist(data[['x', 'y']], data[['x', 'y']])
        edges = [set() for i in range(len(data))]
        for a, b, c in tri.simplices:
            if distances[a,b] < 1:
                edges[a].add(b)
                edges[b].add(a)
            if distances[b,c] < 1:
                edges[a].add(c)
                edges[c].add(a)
            if distances[a,c] < 1:
                edges[b].add(c)
                edges[c].add(b)

        use_values = (data.cell_type=='Macrophage')
        if np.sum(use_values) == 0: return
        values = data.phenotype
        morans_solver = pyGraphStats.MoransSolver(len(data), edges, use_values.to_numpy(), values.to_numpy())

        morans = pd.DataFrame(columns=['N'], dtype=int).set_index('N')
        morans['Morans'] = 0.0
        morans['err'] = 0.0

        for n in range(1,9):
            soln = morans_solver.solve(n)

            mask = (np.array(soln.n_neighbours) > 0) & use_values
            mean_neighbour_values = (np.array(soln.s_neighbours) / np.array(soln.n_neighbours))[mask]
            origin_values = data.phenotype[mask]
            if np.sum(mask) <= 8: continue

            try:
                result = linregress(origin_values, mean_neighbour_values)
                morans.loc[n, 'Morans'] = result.slope
                morans.loc[n, 'err'] = result.stderr
            except Exception as e:
                print(e)
                continue

        ax.plot(morans.index, morans['Morans'], 'kx-')
        ax.fill_between(morans.index, morans['Morans'] + morans['err'], morans['Morans'] - morans['err'])
        
