from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages


def plot_time_domain(data, keys, title):
    fig, axs = plt.subplots(len(data) - 1, 1, tight_layout=True)
    plt.suptitle(title)
    if len(data) > 2:
        for i, ax in enumerate(axs):
            if keys[1 + i] == 'sleep':
                time_plot, data_plot= plot_sleep_stage(data[0], data[1 + i])
                ax.plot(time_plot, data_plot, label=keys[1 + i], color='red')
                ax.legend()
                ax.invert_yaxis()
            else:
                ax.plot(data[0], data[1 + i], label=keys[1 + i])
                ax.legend()
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    else:
        axs.plot(data[0], data[1], label=keys[1])
        axs.legend()
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


def plot_time_domain_single_figure(data, keys, title):
    num = len(data) - 1
    for i in range(num):
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        ax.plot(data[0], data[1 + i], label=keys[1 + i])
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.suptitle(title)


def plot_time_domain_single_figure_combine(data, keys, title):
    num = len(data) - 1
    fig, ax = plt.subplots(1, 1, tight_layout=True)
    for i in range(num):
        ax.plot(data[0], data[1 + i], label=keys[1 + i])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.legend()
    plt.suptitle(title)


def multipage_save(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()


def plot_features(features_final, key_final, title):
    plot_time_domain_single_figure_combine(
        [features_final[0]] + features_final[key_final.index('hr_mean'):key_final.index('hr_min') + 1],
        [key_final[0]] + key_final[key_final.index('hr_mean'):key_final.index('hr_min') + 1],
        title=title)
    plot_time_domain_single_figure_combine(
        [features_final[0]] + features_final[key_final.index('hrv_mean'):key_final.index('hrv_min') + 1],
        [key_final[0]] + key_final[key_final.index('hrv_mean'):key_final.index('hrv_min') + 1],
        title=title)
    plot_time_domain_single_figure_combine(
        [features_final[0]] + features_final[key_final.index('spo2_mean'):key_final.index('spo2_min') + 1],
        [key_final[0]] + key_final[key_final.index('spo2_mean'):key_final.index('spo2_min') + 1],
        title=title)

    plot_time_domain([features_final[0]] + features_final[key_final.index('spo2_min') + 1:],
                     [key_final[0]] + key_final[key_final.index('spo2_min') + 1:], title=title)


def plot_sleep_stage(array_time, array_sleep_stage):
    stage_plot_time = []
    stage_plot_stage = []
    for k in range(1, len(array_time)):
        stage_plot_time.append(array_time[k])
        stage_plot_time.append(array_time[k])
        stage_plot_stage.append(array_sleep_stage[k - 1])
        stage_plot_stage.append(array_sleep_stage[k])
    return stage_plot_time, stage_plot_stage
