import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot as plt

# deprecated
# def buffer2dataframe(buffer):
#     df = pd.DataFrame(buffer)
#     df.colums = ["Time [s]", "Voltage [V]"]
#     return df

def buffers2dataframe(ibuffer, vbuffer):
    """
    @param ibuffer : 2d - array: timestamps, current
    @param vbuffer : 2d - array: timestamps, voltage
    @returns DataFrame: timestamps, current, voltage
    """
    df = pd.DataFrame(np.vstack((ibuffer[:,0], ibuffer[:,1], vbuffer[:,1])).T)
    df.columns = ["Time [s]", "Current [A]", "Voltage [V]"]
    return df

def load_dataframe(p:str):
    """
    Load a dataframe from file.
    @param p : path of the file. If it has 'csv' extension, pandas.read_csv is used, pandas.read_pickle otherwise
    """
    if not path.isfile(p):
        print(f"ERROR: load_dataframe: File does not exist: {p}")
        return None
    if p.endswith(".csv"):
        df = pd.read_csv(p)
    else:
        df = pd.read_pickle(p)
    return df

def plot(data: str or pd.DataFrame or np.ndarray, title="", U=True, I=False):
    """
    Plot recorded data
    @param data: filepath, dataframe or numpy array
    """
    if type(data) == str:
        _data = load_dataframe(data).to_numpy()
    elif type(data) == pd.DataFrame:
        _data = data.to_numpy()
    else:
        _data = data
    print(_data[0])
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("t [s]")
    vax = ax
    iax = ax
    if U and I:
        iax = ax.twinx()
    if U:
        vax = ax
        vax.set_ylabel("U [V]")
        vax.plot(_data[:,0], _data[:,2], color="blue", label="voltage")
    if I:
        iax.set_ylabel("I [A]")
        iax.plot(_data[:,0], _data[:,1], color="orange", label="current")
    if U and I:
        plt.legend()
    return fig





