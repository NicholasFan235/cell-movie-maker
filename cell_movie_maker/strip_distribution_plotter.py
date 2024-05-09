import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline


class StripPressureDistributionPlotter:
    def plot(fig, ax, simulation_timepoint, frame_num, timepoint):
        ax.set_xlabel(f'x-position')
        ax.set_ylabel('Pressure')
        ax.margins(0.01)
        ax.set_title(f'{simulation_timepoint.name}/{simulation_timepoint.id} #{frame_num}, {float(timepoint)/60/24:.1f} days')
        
        data = simulation_timepoint.data[['x', 'pressure']].sort_values('x')
        spl = UnivariateSpline(data.x, data.pressure)
        xs = np.linspace(data.x.min(), data.x.max(), 100)
        ax.plot(data.x, data.pressure, 'kx')
        ax.plot(xs, spl(xs), 'r', lw=3)
        ax.set_ylim(np.floor(np.min(spl(xs))), np.ceil(np.max(spl(xs))))

