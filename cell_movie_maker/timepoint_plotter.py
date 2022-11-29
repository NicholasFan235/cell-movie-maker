

class TimepointPlotter:
    def __init__(self, **plot_kwargs):
        self.plot_kwargs = plot_kwargs
    
    def plot_stroma(self, ax, simulation_timepoint):
        data = simulation_timepoint.stroma_data
        ax.scatter(
            data.x, data.y,
            color='lightblue',
            **self.plot_kwargs)

    def plot_tumour(self, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data
        ax.scatter(
            data.x, data.y,
            cmap='Reds',
            c=1-data.damage,
            vmin=0, vmax=1,
            **self.plot_kwargs)

    def plot_cytotoxic(self, ax, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data
        ax.scatter(
            data.x, data.y,
            cmap='Wistia',
            c=data.potency,
            vmin=0, vmax=1,
            **self.plot_kwargs)

    def plot(self, ax, simulation_timepoint, sim_name, sim_id, frame_num):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.margins(0.01)
        ax.set_title(f'{sim_name}/{sim_id} #{id} t={frame_num/60/24:.1f}d')
        self.plot_stroma(ax, simulation_timepoint)
        self.plot_tumour(ax, simulation_timepoint)
        self.plot_cytotoxic(ax, simulation_timepoint)
    
    def cytotoxic_histogram(self, ax, simulation_timepoint):
        data = simulation_timepoint.cytotoxic_data.potency.to_numpy()
        data[data < 0] = 0
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('CD8+ Potency')
    
    def tumour_histogram(self, ax, simulation_timepoint):
        data = simulation_timepoint.tumour_data.damage.to_numpy()
        data[data > 1] = 1
        ax.hist(data, bins=10, range=(0,1), log=True)
        ax.set_xscale('log')
        ax.set_xlabel('Tumour Accumulated Damage')
