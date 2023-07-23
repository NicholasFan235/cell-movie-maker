import matplotlib.pylab as plt
import matplotlib as mpl
import os
import pathlib
import re
import tqdm
import multiprocessing


class SVGStitcher:
    def __init__(self, simulation, output_parent_folder='visualisations', visualisation_name='abstract-svg-stitch'):
        self.visualisation_name = visualisation_name
        self.sim = simulation

        self.vis_folder = pathlib.Path(output_parent_folder, self.sim.name, self.sim.id)
        self.output_folder = pathlib.Path(self.vis_folder, visualisation_name)
        self.probe_vis_type = 'tcell-svg-png'

        self.figsize=(16,8)

    def process_frame(self, n):
        raise NotImplementedError

    def n_frames(self, vis_type):
        folder = pathlib.Path(self.vis_folder, vis_type)
        if not folder.exists(): return 0
        r = re.compile('^frame_\d+\.png')
        files = list(map(lambda s: int(s.lstrip('frame_').rstrip('.png')), filter(r.match, os.listdir(folder))))
        return len(files)

    def get_frame(self, vis_type, n):
        folder = pathlib.Path(self.vis_folder, vis_type)
        if not folder.exists(): raise FileNotFoundError
        return plt.imread(pathlib.Path(folder, f'frame_{n}.png'))

    def run(self, start=0, stop=None, step=1, maxproc=64):
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True, exist_ok=True)
        
        max_n = self.n_frames(self.probe_vis_type)
        if stop is None: stop = max_n
        else: stop = min(max_n, stop)
        
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
            _=list(tqdm.tqdm(pool.imap(self.process_frame, range(start, stop, step)),
                             total=(stop-start)//step))

    def prepare(self, pattern, n):
        simulation_timepoint = self.sim.read_timepoint(self.sim.results_timesteps[n])
        fig, axs = plt.subplot_mosaic(pattern, figsize=self.figsize)
        for k in axs: axs[k].set_xticks([])
        for k in axs: axs[k].set_yticks([])
        return fig, axs, simulation_timepoint
    
    def post(self, fig, axs, n):
        fig.tight_layout()
        fig.savefig(os.path.join(self.output_folder, f'frame_{n}.png'))
        plt.close(fig)
    
    def plot_oxygen(self, fig, ax, simulation_timepoint):
        ax.set_title('Oxygen')
        oxygen_data = simulation_timepoint.oxygen_data
        if oxygen_data is not None:
            ox = ax.imshow(oxygen_data, cmap='cividis', vmin=0, vmax=1, origin='lower')
            fig.colorbar(ox, ax=ax)
    
    def plot_ccl5(self, fig, ax, simulation_timepoint):
        ax.set_title('CCL5 (Chemoattractant)')
        ccl5data = simulation_timepoint.ccl5_data
        if ccl5data is not None:
            ccl5 = ax.imshow(ccl5data, cmap='magma', vmin=0, vmax=ccl5data.max(), origin='lower')
            fig.colorbar(ccl5, ax=ax)

    def plot_ifng(self, fig, ax, simulation_timepoint):
        ax.set_title('IFN-g (Produced by activated T-cells)')
        ifng_data = simulation_timepoint.ifng_data
        if ifng_data is not None:
            ifng = ax.imshow(simulation_timepoint.ifng_data, cmap='binary', vmin=0, vmax=1, origin='lower')
            fig.colorbar(ifng, ax=ax)

    def plot_cxcl9(self, fig, ax, simulation_timepoint):
        ax.set_title('CXCL-9 (Reduce T-cell motility)')
        cxcl9_data = simulation_timepoint.cxcl9_data
        if cxcl9_data is not None:
            cxcl9 = ax.imshow(cxcl9_data, cmap='binary', vmin=0, vmax=1, origin='lower')
            fig.colorbar(cxcl9, ax=ax)

    def plot_ecm_density(self, fig, ax, simulation_timepoint):
        ax.set_title('ECM Density')
        ecm_density_data = simulation_timepoint.ecm_density_data
        if ecm_density_data is not None:
            density = ax.imshow(ecm_density_data, cmap='binary', vmin=0, vmax=1, origin='lower')
            fig.colorbar(density, ax=ax)

class TCellSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tcell-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)

        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        self.plot_ccl5(fig, axs['C'], simulation_timepoint)
        self.plot_ifng(fig, axs['D'], simulation_timepoint)
        self.plot_cxcl9(fig, axs['E'], simulation_timepoint)
        self.post(fig, axs, n)

class TumourSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tumour-stitched', p_max=10, *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.p_max = p_max

    def process_frame(self, n):
        fig, axs, simulation_timepoint = self.prepare("AABC;AADE", n)
        
        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)
        self.plot_oxygen(fig, axs['B'], simulation_timepoint)
        axs['C'].set_title('Pressure')
        axs['C'].imshow(self.get_frame('pressure-svg-png', n))
        plt.colorbar(mpl.cm.ScalarMappable(cmap='cividis', norm=mpl.colors.Normalize(vmin=0, vmax=self.p_max)), ax=axs['C'])
        self.plot_ccl5(fig, axs['D'], simulation_timepoint)
        self.plot_ecm_density(fig, axs['E'], simulation_timepoint)
        self.post(fig, axs, n)
    