import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from time import sleep
from random import choice as r_choice

if __name__ == "__main__":
    if __package__ is None:
        # make relative imports work as described here: https://peps.python.org/pep-0366/#proposed-change
        __package__ = "k-teng"
        import sys
        from os import path
        filepath = path.realpath(path.abspath(__file__))
        sys.path.insert(0, path.dirname(path.dirname(filepath)))
from .utility.data import load_dataframe

file = "/home/matth/data/gel_big_gap000.csv"

class PeakInfo:
    """
    Helper class for "iterating" through selected peaks.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self._peak_names = [ "first", "second", "last", "lowest" ]
        self._peaks = { p: None for p in self._peak_names }
        self._iter = 0

    def current(self):
        # return (self._peak_names[self._iter]), self._peaks[self._peak_names[self._iter]]
        return self._peaks[self._peak_names[self._iter]]
    def name(self):
        return self._peak_names[self._iter]

    def next(self):
        if self._iter < len(self._peak_names) - 1: self._iter += 1
        return self.current()
    def prev(self):
        if self._iter > 0: self._iter -= 1
        return self.current()

    def set(self, value):
        """Assign a value to the crrent peak"""
        self._peaks[self._peak_names[self._iter]] = value
    def is_done(self):
        for peak in self._peaks.values():
            if peak is None: return False
        return True

    def __getitem__(self, key):
        return self._peaks[key]
    def __setitem__(self, key, value):
        self._peaks[key] =  value
    def __repr__(self):
        return f"{self._peak_names[self._iter]} peak"



def find_peaks(a):
    peaks = signal.find_peaks(a)


def on_click(fig, ax, peaks, event):
    """
    Let the user select first, second and last peak by clicking on them in this order.
    Right click undos the last selection
    """
    select = None
    if event.button == 1:  # left click
        peaks.set((event.xdata, event.ydata))
        print(f"{peaks}: {event.xdata} - {event.ydata}")
        ax.set_title(f"{peaks}: {event.xdata} - {event.ydata}")
        peaks.next()
    elif event.button == 3:  # right click
        ax.set_title(f"Undo {peaks.name()}")
        if not peaks.is_done():
            peaks.prev()
        peaks.set(None)
    if peaks.is_done(): message = "Close window when done"
    else: message = f"Click on {peaks}"
    fig.suptitle(message)
    fig.canvas.draw()
    # fig1.canvas.flush_events()

def calc_peaks(peaks):
    # get the peak points from the information of a Peaks object
    # 90% distance between first and second
    min_distance = max(1, (peaks["second"][0] - peaks["first"][0]) * 0.9)
    min_height = peaks["lowest"][1] * 0.99
    vpeaks = signal.find_peaks(vdata, height=min_height, distance=min_distance)
    return vpeaks


class Normalize:
    """
    normalize so that all values are between low and high
    """
    def __init__(self, low=0, high=1):
        assert(low < high)
        self.low = low
        self.high = high
    def __call__(self, array):
        min_ = np.min(array)
        a = a - min_
        max_ = np.max(array)
        if max_ != 0:
            a = (a / max_)
        # now normalized between 0 and 1
        a *= (self.high - self.low)
        a -= self.low
        return a

if __name__ == "__main__":
    """
    Peak identification:
    plot, let user choose first, second, last and lowest peak for identification
    """
    df = load_dataframe(file)
    a = df.to_numpy()
    vdata = Normalize(0, 1)(a[:,2])
    plt.ion()
    # vpeaks[0] is the list of the peaks
    vpeaks = signal.find_peaks(vdata)[0]
    fig, ax = plt.subplots()
    ax.plot(vdata)
    peak_lines = ax.vlines(vpeaks, 0, 1, colors="r")
    ax.grid(True)
    fig.suptitle("Click on first peak")
    peak_info = PeakInfo()
    # handle clicks
    fig.canvas.mpl_connect("button_press_event", lambda ev: on_click(fig, ax, peak_info, ev))
    # run until user closes, events are handled with on_click function
    print(vdata.size)
    while plt.fignum_exists(fig.number):
        plt.pause(0.01)
        if (peak_info.is_done()):
            vpeaks = calc_peaks(peak_info)[0]
            x_margin = (a[-1,0] - a[0,0]) * 0.05   # allow some margin if user clicked not close enough on peak
            vpeaks = vpeaks[(vpeaks >= peak_info["first"][0] - x_margin) & (vpeaks <= peak_info["last"][0] + x_margin)]   # remove peaks before first and after last
            peak_lines.remove()
            peak_lines = ax.vlines(vpeaks, 0, 1, colors="r")
            peak_info.reset()
    print(a[:,0], vpeaks)

    # separate peaks
    indices = np.arange(0, a[:,0].size)
    peak_datas = []
    for i in range(len(vpeaks) - 1):
        # TODO: user <= or <
        peak_datas.append(vdata[(indices >= vpeaks[i]) & (indices < vpeaks[i+1])])
        plt.plot(peak_datas[i])
    print(peak_datas)
    plt.pause(20)



