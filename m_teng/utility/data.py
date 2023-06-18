import pandas as pd
import numpy as np
from os import path

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
