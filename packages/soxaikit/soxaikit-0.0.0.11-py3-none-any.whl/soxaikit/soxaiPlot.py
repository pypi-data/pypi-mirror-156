from matplotlib import pyplot as plt
import matplotlib.dates as mdates


def plot_time_domain(data, keys):
    fig, axs = plt.subplots(len(data) - 1, 1, tight_layout=True)
    if len(data) > 2:
        for i, ax in enumerate(axs):
            ax.plot(data[0], data[1 + i], label=keys[1 + i])
            ax.legend()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    else:
        axs.plot(data[0], data[1], label=keys[1])
        axs.legend()
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
