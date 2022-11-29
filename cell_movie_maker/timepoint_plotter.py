

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

    def plot(self, ax, simulation_timepoint):
        self.plot_stroma(ax, simulation_timepoint)
        self.plot_tumour(ax, simulation_timepoint)
        self.plot_cytotoxic(ax, simulation_timepoint)
