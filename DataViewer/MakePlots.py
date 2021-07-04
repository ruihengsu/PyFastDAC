"""
Author: Ruiheng Su

Engineering Physics, UBC

ruihengsu@alumni.ubc.ca

2020
"""

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import scipy.signal as ss


def apply_smoothing(df, window=5, polyorder=2, inplace=False):
    """
    Wrapper on the savgol filter applied to column 1 of a data frame

    @param df: a pandas dataframe consisting of two columns numbered 0 and 1

    @param window: the number of the data points to average at a time

    @param polyorder; the degree of the polynomial used to
           interpolate the data

    @param inplace: directly modifies the data frame if true; returns a new
           new copy otherwise

    @return a pandas data frame with column 1 values smoothed
    """
    if not inplace:
        new = df.copy()
        new.loc[:, new.columns[1]] = ss.savgol_filter(
            new.loc[:, new.columns[1]], window, polyorder)
        return new
    else:
        df.loc[:, df.columns[1]] = ss.savgol_filter(
            df.loc[:, df.columns[1]], window, polyorder)
        return df


def add_to_figure(data, name, fig=None, scale=1, x=0, keep=0.3, smoothing=7,
                  polyorder=1, peak_height=None, peak_samples=None, peak_num=None,
                  peak_offset=None):
    """

    """
    if data is None:
        return go.Figure()

    if fig == None:
        fig = go.Figure()

    fig.update_layout(xaxis_title='',
                      yaxis_title='',
                      xaxis=dict(
                          rangeslider=dict(
                              visible=False),)
                      )

    # step = int(1/keep)
    time = np.linspace(0, len(data), num = len(data))
    # time = time[::step]
    # signal = data[::step]*scale
    signal = data*scale

    # if smoothing != 1:
    #     signal = ss.savgol_filter(signal, smoothing, polyorder)

    fig.add_trace(
        go.Scatter(
            x=time,
            y=signal,
            mode='lines',
            name=name,
            legendgroup=name,
            opacity=0.6,
        )
    )

    # if peak_height is not None and peak_samples is not None:
    #     peaks = ss.find_peaks(
    #         signal, height=peak_height, distance=peak_samples)[0]

    #     fig.add_trace(go.Scatter(x=time[peaks],
    #                              y=signal[peaks],
    #                              mode='markers',
    #                              marker=dict(size=10,
    #                                          symbol='cross'),
    #                              name=name+" Peaks",
    #                              legendgroup=name+" Peaks"))

    #     if peak_num is not None:

    #         peak_offset -= 50
    #         peak_offset *= (1/100.)

    #         min_index = peaks[peak_num] - peak_samples + \
    #             int(peak_samples*peak_offset)
    #         max_index = peaks[peak_num] + peak_samples + \
    #             int(peak_samples*peak_offset)

    #         if min_index < 0:
    #             min_index = 0
    #         if max_index > len(time):
    #             max_index = len(time) - 1

    #         xmin = time[min_index]
    #         xmax = time[max_index]

    #         fig.update_layout(xaxis_range=[xmin, xmax])

    #     return fig, len(peaks)

    return fig, 0
