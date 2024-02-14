import pathlib
import cell_movie_maker.svg
import multiprocessing
import matplotlib.pylab as plt
import tqdm
import re
import os
import math


class AbstractMultisimStitcher:
    def __init__(self, simulations, output_parent_folder='visualisations', visualisation_name='abstract-multisim-stitch', n_rows=1):
        self.visualisation_name = visualisation_name
        self.sims = list(simulations)

        self.output_parent_folder = output_parent_folder
        self.vis_folder = pathlib.Path(output_parent_folder, self.sims[0].name)
        self.output_folder = pathlib.Path(self.vis_folder, visualisation_name)
        self.probe_vis_type = 'tcell-svg-png'
        self.n_rows = n_rows
        self.postprocess = None

        self.resize(6)
    
    def resize(self, unit_width=6):
        self.figsize=(unit_width*math.ceil(len(self.sims)/self.n_rows), unit_width*self.n_rows)

    def process_frame(self, n):
        fig, axs = self.prepare()

        for i, sim in enumerate(self.sims):
            self.plot_simulation(fig, axs[i], sim, n)

        self.post(fig, axs, n)

    def plot_simulation(self, fig, ax, simulation, n):
        raise NotImplementedError

    def n_frames(self, sim, vis_type):
        folder = pathlib.Path(self.output_parent_folder, sim.name, sim.id, vis_type)
        if not folder.exists(): return 0
        r = re.compile('^frame_\d+\.png')
        files = list(map(lambda s: int(s.lstrip('frame_').rstrip('.png')), filter(r.match, os.listdir(folder))))
        return len(files)

    def get_frame(self, sim, vis_type, n):
        folder = pathlib.Path(self.output_parent_folder, sim.name, sim.id, vis_type)
        if not folder.exists(): raise FileNotFoundError
        n = min(n, self.n_frames(sim, vis_type)-1)
        return plt.imread(pathlib.Path(folder, f'frame_{n}.png'))

    def run(self, start=0, stop=None, step=1, maxproc=64):
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True, exist_ok=True)
        
        max_n = 0
        for sim in self.sims: max_n = max(max_n, self.n_frames(sim, self.probe_vis_type))
        if stop is None: stop = max_n
        else: stop = min(max_n, stop)
        
        if maxproc > 1:
            with multiprocessing.Pool(processes=min(multiprocessing.cpu_count()-1, maxproc)) as pool:
                _=list(tqdm.tqdm(pool.imap(self.process_frame, range(start, stop, step)),
                                 total=(stop-start)//step))
        else:
            for i in tqdm.tqdm(range(start, stop, step), total=(stop-start)//step):
                self.process_frame(i)

    def prepare(self):
        fig, axs = plt.subplots(self.n_rows, math.ceil(len(self.sims)/self.n_rows), figsize=self.figsize,
                                layout="constrained")
        return fig, axs.reshape(-1)
    
    def post(self, fig, axs, n):
        #fig.tight_layout()
        if self.postprocess is not None: self.postprocess(fig, axs, n)
        fig.savefig(os.path.join(self.output_folder, f'frame_{n}.png'))
        plt.close(fig)


