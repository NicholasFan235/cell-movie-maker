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

class TCellSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tcell-stitched', *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
    
    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def process_frame(self, n):
        simulation_timepoint = self.sim.read_timepoint(self.sim.results_timesteps[n])

        fig, axs = plt.subplot_mosaic("AABC;AADE", figsize=self.figsize)
        for k in axs: axs[k].set_xticks([])
        for k in axs: axs[k].set_yticks([])

        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        axs['B'].set_title('Oxygen')
        ox = axs['B'].imshow(simulation_timepoint.oxygen_data, cmap='cividis', vmin=0, vmax=1, origin='lower')
        fig.colorbar(ox, ax=axs['B'])

        axs['C'].set_title('CCL5 (Chemoattractant)')
        ccl5data = simulation_timepoint.ccl5_data
        ccl5 = axs['C'].imshow(ccl5data, cmap='magma', vmin=0, vmax=ccl5data.max(), origin='lower')
        fig.colorbar(ccl5, ax=axs['C'])

        axs['D'].set_title('IFN-g (Produced by activated T-cells)')
        ifng = axs['D'].imshow(simulation_timepoint.ifng_data, cmap='binary', vmin=0, vmax=1, origin='lower')
        fig.colorbar(ifng, ax=axs['D'])

        axs['E'].set_title('CXCL-9 (Reduce T-cell motility)')
        cxcl9 = axs['E'].imshow(simulation_timepoint.cxcl9_data, cmap='binary', vmin=0, vmax=1, origin='lower')
        fig.colorbar(cxcl9, ax=axs['E'])

        fig.tight_layout()
        fig.savefig(os.path.join(self.output_folder, f'frame_{n}.png'))
        plt.close(fig)

class TumourSVGStitcher(SVGStitcher):
    def __init__(self, simulation, visualisation_name='tumour-stitched', p_max=10, *args, **kwargs):
        super().__init__(simulation, visualisation_name=visualisation_name, *args, **kwargs)
        self.p_max = p_max

    def process_frame(self, n):
        simulation_timepoint = self.sim.read_timepoint(self.sim.results_timesteps[n])

        fig, axs = plt.subplot_mosaic("AABC;AADE", figsize=self.figsize)
        for k in axs: axs[k].set_xticks([])
        for k in axs: axs[k].set_yticks([])
        
        axs['A'].imshow(self.get_frame('tcell-svg-png', n))
        axs['A'].set_title(f'{self.sim.name}/{self.sim.id} #{n}', fontsize=30)

        axs['B'].set_title('Oxygen')
        axs['B'].set_yticks([])
        axs['B'].set_xticks([])
        ox = axs['B'].imshow(simulation_timepoint.oxygen_data, cmap='cividis', vmin=0, vmax=1, origin='lower')
        fig.colorbar(ox, ax=axs['B'])

        axs['C'].set_title('Pressure')
        axs['C'].imshow(self.get_frame('pressure-svg-png', n))
        plt.colorbar(mpl.cm.ScalarMappable(cmap='cividis', norm=mpl.colors.Normalize(vmin=0, vmax=self.p_max)), ax=axs['C'])

        axs['D'].set_title('CCL5 (Chemoattractant)')
        ccl5data = simulation_timepoint.ccl5_data
        ccl5 = axs['D'].imshow(ccl5data, cmap='magma', vmin=0, vmax=100, origin='lower')
        fig.colorbar(ccl5, ax=axs['D'])

        axs['E'].set_title('ECM Density')
        ecm_density_data = simulation_timepoint.ecm_density_data
        density = axs['E'].imshow(ecm_density_data, cmap='binary', vmin=0, vmax=1, origin='lower')
        fig.colorbar(density, ax=axs['E'])

        fig.tight_layout()
        fig.savefig(os.path.join(self.output_folder, f'frame_{n}.png'))
        plt.close(fig)
    