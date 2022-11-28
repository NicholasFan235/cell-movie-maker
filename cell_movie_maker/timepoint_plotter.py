

class TimepointPlotter:
    def __init__(self, **plot_kwargs):
        self.plot_kwargs = plot_kwargs
    
    def plot_stroma(self, ax, simulation_timepoint):
        sel = simulation_timepoint.data.potency == -1
        ax.scatter(
            simulation_timepoint.data.loc[sel, 'x'],
            simulation_timepoint.data.loc[sel, 'y'],
            color='lightblue',
            **self.plot_kwargs)

    def plot_tumour(self, ax, simulation_timepoint):
        sel = simulation_timepoint.data.potency == -2
        ax.scatter(
            simulation_timepoint.data.loc[sel, 'x'],
            simulation_timepoint.data.loc[sel, 'y'],
            cmap='Reds',
            c=1-simulation_timepoint.data.loc[sel, 'damage'],
            vmin=0, vmax=1,
            **self.plot_kwargs)

    def plot_cytotoxic(self, ax, simulation_timepoint):
        sel = simulation_timepoint.data.potency >= 0
        ax.scatter(
            simulation_timepoint.data.loc[sel, 'x'],
            simulation_timepoint.data.loc[sel, 'y'],
            cmap='Wistia',
            c=simulation_timepoint.data.loc[sel, 'potency'],
            vmin=0, vmax=1,
            **self.plot_kwargs)

    def plot(self, ax, simulation_timepoint):
        self.plot_stroma(ax, simulation_timepoint)
        self.plot_tumour(ax, simulation_timepoint)
        self.plot_cytotoxic(ax, simulation_timepoint)
