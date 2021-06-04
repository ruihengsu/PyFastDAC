from os import read
import time
import pickle
import numpy as np

from pathlib import Path
from datetime import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.linewidth'] = 2
plt.rcParams.update({'font.size': 12,
                     'figure.autolayout': True})


def new_simple_figure(figsize):
    """Returns a figure and an axis object

    Parameters
    ----------
    figsize : tuple
        Example: (6,4)
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.tick_params(axis="y", direction="in", length=4)
    ax.tick_params(axis="x", direction="in", length=4)
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')
    return fig, ax


def plot_PID_readings(fd, reading, setting, sampling_period = None, xlabel="Samples", ylabel="Voltage [mV]", save=False, figsize=(6, 4), lw=2.2, separate=False, title="", comment = ""):
    """Plots a PID recording

    Parameters
    ----------

    fd : PIDFastDAC object 

    reading : dict 
        A dictionary. Keys will be used in plot legend. The values are numpy arrays

    setting : dict 
        A dictionary of the settings used to produce the data

    sampling_period : None or float, optional
        The delta_t between two samples 

    xlabels : str, optional 
        The label of the horizontal axis 

    ylabel : str, optional 
        The label of the vertical axis 

    save : bool, optional 
        Whether to save the plots, `reading`, `setting`

    figsize : tuple, optional 

    lw : float, optional 
        the linewidth of the curves 

    separate : bool, optional 
        Whether to plot all the curves in the same plot, or as separate plots 
    """
    if comment:
        setting["comment"] = comment

    if save:
        save_dir = save_PID_recording(fd, reading, setting)

    if separate:
        for ac in reading.keys():
            fig, ax = new_simple_figure(figsize)
            if sampling_period is not None: 
                time = np.array([sampling_period*i for i in range(0, len(reading[ac]))])
                ax.plot(time, reading[ac], label="{}".format(ac), linewidth=lw)
            else:
                ax.plot(reading[ac], label="{}".format(ac), linewidth=lw)
            plt.tight_layout()
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.legend()
            if not save:
                plt.show()
            else:
                plt.savefig(save_dir + "/{}.pdf".format(ac))
    else:
        fig, ax = new_simple_figure(figsize)
        for ac in reading.keys():
            if sampling_period is not None: 
                time = np.array([sampling_period*i for i in range(0, len(reading[ac]))])
                ax.plot(time, reading[ac], label="{}".format(ac), linewidth=lw)
            else:
                ax.plot(reading[ac], label="{}".format(ac), linewidth=lw)
        plt.tight_layout()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        if not save:
            plt.show()
        else:
            plt.savefig(save_dir + "/{}.pdf".format("_".join(str(ac)
                        for ac in reading.keys())))


def plot_readings(reading, xlabel="Samples", ylabel="Voltage [mV]", figsize=(6, 4), lw=2.2, separate=False, title=""):
    """Parses a dictionary containing numpy arrays as values and plots them. 

    Parameters
    ----------
    reading : dict 
        A dictionary. Keys will be used in plot legend. The values are numpy arrays

    xlabels : str, optional 
        The label of the horizontal axis 

    ylabel : str, optional 
        The label of the vertical axis 

    figsize : tuple, optional 

    lw : float, optional 
        the linewidth of the curves 

    separate : bool, optional 
        Whether to plot all the curves in the same plot, or as separate plots 
    """

    if separate:
        for ac in reading.keys():
            fig, ax = new_simple_figure(figsize)
            ax.plot(reading[ac], label="{}".format(ac), linewidth=lw)
            plt.tight_layout()
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            plt.legend()
            plt.show()
    else:
        fig, ax = new_simple_figure(figsize)
        for ac in reading.keys():
            ax.plot(reading[ac], label="{}".format(ac), linewidth=lw)
        plt.tight_layout()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.show()

def save_PID_recording(fd, concat_reading, settings):
    """ Dump `concat_reading` and `setting` to pickle files for future analysis. 
    """
    now = datetime.today().strftime('%Y%m%d')
    save_to = fd.datapath + "/{}".format(now)
    Path(save_to).mkdir(parents=True, exist_ok=True)

    # count the number of PID directories
    count = 0
    for path in Path(save_to).iterdir():
        if not path.is_file():
            count += 1

    kp = fd.kp
    ki = fd.ki
    kd = fd.kd
    slew = fd.slew

    save_to_sub = save_to + \
        "/PID[{}]_P[{}]_I[{}]_D[{}]_SR[{}]".format(count, kp, ki, kd, slew)
    Path(save_to_sub).mkdir(parents=True, exist_ok=True)

    with open("{}.pickle".format(save_to_sub + "/PID"), "wb") as write_to:
        pickle.dump(concat_reading, write_to)

    if settings is not None:
        with open("{}.pickle".format(save_to_sub + "/settings"), "wb") as write_to:
            pickle.dump(settings, write_to)

    print("Data saved to {}".format(save_to_sub))

    return save_to_sub
