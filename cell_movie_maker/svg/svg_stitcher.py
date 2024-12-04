import matplotlib.pylab as plt
import matplotlib as mpl
import os
import pathlib
import re
import tqdm
import multiprocessing
import pandas as pd
from ..simulation_timepoint import SimulationTimepoint


class SVGStitcher:
    def __init__(self, simulation, output_parent_folder='visualisations', visualisation_name='abstract-svg-stitch'):
        self.visualisation_name = visualisation_name
        self.sim = simulation

        self.vis_folder = pathlib.Path(output_parent_folder, self.sim.name, self.sim.id)
        self.output_folder = pathlib.Path(self.vis_folder, visualisation_name)
        self.probe_vis_type = 'tcell-svg-png'

        self.figsize=(16,8)
        self.ccl5_max=None
        self.ifng_max=None
        self.cxcl9_max=None
        self.automated_post=True

    def process_frame(self, n):
        raise NotImplementedError

    def n_frames(self, vis_type):
        folder = pathlib.Path(self.vis_folder, vis_type)
        if not folder.exists(): return 0
        r = re.compile(r'^frame_\d+\.png')
        files = list(map(lambda s: int(s.lstrip('frame_').rstrip('.png')), filter(r.match, os.listdir(folder))))
        return len(files)

    def get_frame(self, vis_type, n):
        folder = pathlib.Path(self.vis_folder, vis_type)
        if not folder.exists(): raise FileNotFoundError
        n = min(n, self.n_frames(vis_type)-1)
        return plt.imread(pathlib.Path(folder, f'frame_{n}.png'))

    def run(self, start=0, stop=None, step=1, maxproc=64):
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True, exist_ok=True)
        
        max_n = self.n_frames(self.probe_vis_type)
        if stop is None: stop = max_n
        else: stop = min(max_n, stop)
        
        if maxproc > 1:
            with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
                _=list(tqdm.tqdm(pool.imap(self.process_frame, range(start, stop, step)),
                                 total=(stop-start)//step))
        else:
            for i in tqdm.tqdm(range(start, stop, step), total=(stop-start)//step):
                self.process_frame(i)

    def prepare(self, pattern, n):
        simulation_timepoint = self.sim.read_timepoint(self.sim.results_timesteps[n])
        fig, axs = plt.subplot_mosaic(pattern, figsize=self.figsize)
        return fig, axs, simulation_timepoint
    
    def post(self, fig, axs, n):
        if self.automated_post:
            fig.tight_layout()
            fig.savefig(os.path.join(self.output_folder, f'frame_{n}.png'))
            plt.close(fig)
        else:
            return fig, axs
    
    def plot_oxygen(self, fig, ax, simulation_timepoint):
        ax.set_title('Oxygen')
        ax.set_xticks([])
        ax.set_yticks([])
        oxygen_data = simulation_timepoint.oxygen_data
        if oxygen_data is not None:
            ox = ax.imshow(oxygen_data, cmap='cividis', vmin=0, vmax=1)
            fig.colorbar(ox, ax=ax)
    
    def plot_ccl5(self, fig, ax, simulation_timepoint):
        ax.set_title('CCL5 (Chemoattractant)')
        ax.set_xticks([])
        ax.set_yticks([])
        ccl5data = simulation_timepoint.ccl5_data
        if ccl5data is not None:
            ccl5 = ax.imshow(ccl5data, cmap='magma', vmin=0, vmax=self.ccl5_max if self.ccl5_max is not None else ccl5data.max())
            fig.colorbar(ccl5, ax=ax)

    def plot_ifng(self, fig, ax, simulation_timepoint):
        ax.set_title('IFN-g (Produced by activated T-cells)')
        ax.set_xticks([])
        ax.set_yticks([])
        ifng_data = simulation_timepoint.ifng_data
        if ifng_data is not None:
            ifng = ax.imshow(simulation_timepoint.ifng_data, cmap='binary', vmin=0, vmax=self.ifng_max if self.ifng_max is not None else ifng_data.max())
            fig.colorbar(ifng, ax=ax)

    def plot_cxcl9(self, fig, ax, simulation_timepoint):
        ax.set_title('CXCL-9 (Reduce T-cell motility)')
        ax.set_xticks([])
        ax.set_yticks([])
        cxcl9_data = simulation_timepoint.cxcl9_data
        if cxcl9_data is not None:
            cxcl9 = ax.imshow(cxcl9_data, cmap='binary', vmin=0, vmax=self.cxcl9_max if self.cxcl9_max is not None else cxcl9_data.max())
            fig.colorbar(cxcl9, ax=ax)

    def plot_ecm_density(self, fig, ax, simulation_timepoint):
        ax.set_title('ECM Density')
        ax.set_xticks([])
        ax.set_yticks([])
        ecm_density_data = simulation_timepoint.ecm_density_data
        if ecm_density_data is not None:
            density = ax.imshow(ecm_density_data, cmap='binary', vmin=0, vmax=1)
            fig.colorbar(density, ax=ax)
    
    def plot_tumour_count(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('N-Tumour cells')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.fill_between(info.index/60/24, info['n_tumour'], color='purple', label='Healthy')
        ax.fill_between(info.index/60/24, info['n_tumour_hypoxic'], color='mediumpurple', label='Hypoxic')
        ax.fill_between(info.index/60/24, info['n_tumour_necrotic'], color='white', label='Necrotic')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')

    def plot_tumour_damage_count(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('N-Tumour cells')
        cmap = plt.get_cmap('Purples')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.fill_between(info.index/60/24, info['n_tumour'], color=cmap(0.99), label='0% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage10'], color=cmap(0.8), label='10% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage20'], color=cmap(0.6), label='20% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage40'], color=cmap(0.4), label='60% Damaged')
        ax.fill_between(info.index/60/24, info['n_tumour_damage80'], color=cmap(0.2), label='80% Damaged')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_tumour'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_tumour'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_tumour'], info.n_tumour.max()])
        #ax.set_ylabel('N Cells')
        ax.set_xlabel('Time /days')
    
    def plot_tcell_count(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('N T-Cells')
        cmap = plt.get_cmap('Oranges')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.plot(info.index/60/24, info['n_t-cells'], '-k')
        ax.fill_between(info.index/60/24, info['n_t-cells'], color=cmap(0.99))
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_t-cells'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_t-cells'], info['n_t-cells'].max()])
    
    def plot_tcell_exhaustion_count(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('T-Cell Exhaustion')
        cmap = plt.get_cmap('Oranges')
        if not hasattr(self, 'info'): info = pd.read_csv(pathlib.Path(self.vis_folder, 'info.csv')).set_index('timestep')
        ax.fill_between(info.index/60/24, info['n_t-cells'], color=cmap(0.99), label='0% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency90'], color=cmap(0.8), label='10% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency80'], color=cmap(0.6), label='20% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency60'], color=cmap(0.4), label='40% Exhausted')
        ax.fill_between(info.index/60/24, info['n_t-cells_potency20'], color=cmap(0.2), label='80% Exhausted')
        ax.legend(loc='upper left')
        ax.plot(info.index/60/24, info['n_t-cells'], '-k')
        ax.plot(simulation_timepoint.timestep/60/24, info.loc[simulation_timepoint.timestep, 'n_t-cells'], 'ro')
        ax.set_yticks([0, info.loc[simulation_timepoint.timestep, 'n_t-cells'], info['n_t-cells'].max()])
        ax.set_xlabel('Time /days')

    def plot_tcell_exhaustion_histogram(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('Exhaustion Distribution')
        ax.hist(simulation_timepoint.cytotoxic_data.potency, bins=10, range=(0,1), log=True)
        ax.set_xscale('linear')
        ax.invert_xaxis()
        ax.set_xlabel('CD8+ Potency')
    
    def plot_tumour_damage_histogram(self, fig, ax, simulation_timepoint:SimulationTimepoint):
        ax.set_title('Tumour Damage Distribution')
        ax.hist(simulation_timepoint.tumour_data.damage, bins=10, range=(0,1), log=True)
        ax.set_xscale('linear')
        ax.set_xlabel('Tumour Damage')


class TCellSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tcell-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)

        axs['A'].imshow(self.get_frame('tcell-svg-png', n), origin='lower')
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        self.plot_ccl5(fig, axs['C'], simulation_timepoint)
        self.plot_tumour_damage_count(fig, axs['D'], simulation_timepoint)
        self.plot_tcell_exhaustion_count(fig, axs['E'], simulation_timepoint)
        return self.post(fig, axs, n)


class TCellSVGStitcherCXCL9IFNg(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tcell-cxcl9-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(20,8)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABCD;AAEFG", n)

        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        self.plot_ccl5(fig, axs['C'], simulation_timepoint)
        self.plot_ifng(fig, axs['E'], simulation_timepoint)
        self.plot_cxcl9(fig, axs['F'], simulation_timepoint)
        self.plot_tumour_damage_count(fig, axs['D'], simulation_timepoint)
        self.plot_tcell_exhaustion_count(fig, axs['G'], simulation_timepoint)
        return self.post(fig, axs, n)

class TumourSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tumour-stitched', p_max=10, p_min=0, p_cmap='inferno', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.p_max = p_max
        self.p_min = p_min
        self.p_cmap = p_cmap

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)
        
        axs['A'].imshow(self.get_frame('hypoxia-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)
        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        axs['C'].set_title('Pressure')
        axs['C'].imshow(self.get_frame('pressure-svg-png', n))
        axs['C'].set_xticks([])
        axs['C'].set_yticks([])
        plt.colorbar(mpl.cm.ScalarMappable(cmap=self.p_cmap, norm=mpl.colors.Normalize(vmin=self.p_min, vmax=self.p_max)), ax=axs['C'])
        self.plot_ccl5(fig, axs['D'], simulation_timepoint)
        self.plot_tumour_count(fig, axs['E'], simulation_timepoint)
        return self.post(fig, axs, n)

class TCellSVGStitcherExhaustion(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tcell-exhaustion-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.figsize=(16,8)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AAED", n)

        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_xticks([])
        axs['A'].set_yticks([])
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        self.plot_ccl5(fig, axs['E'], simulation_timepoint)
        self.plot_tumour_damage_count(fig, axs['C'], simulation_timepoint)
        self.plot_tcell_exhaustion_count(fig, axs['D'], simulation_timepoint)
        #self.plot_tumour_damage_histogram(fig, axs['F'], simulation_timepoint)
        #self.plot_tcell_exhaustion_histogram(fig, axs['G'], simulation_timepoint)
        return self.post(fig, axs, n)



