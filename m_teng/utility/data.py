import pandas as pd
import numpy as np
from os import path
import matplotlib.pyplot

def buffer2dataframe(buffer):
    df = pd.DataFrame(buffer)
    df.colums = ["Time [s]", "Voltage [V]"]
    return df

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


def plot(data):
    if type(data) == str:
        data = load_dataframe(data)
    if type(data) == pd.Dataframe:
        data = data.to_numpy()
    fig1, (vax, iax) = plt.subplots(2, 1, figsize=(8, 5))
    # todo


    vline, = vax.plot(index, vdata, color="m")
    vax.set_ylabel("Voltage [V]")
    vax.grid(True)

    vax.plot()

    iline, = iax.plot(index, idata, color="m")
    iax.set_ylabel("Current [A]")
    iax.grid(True)
