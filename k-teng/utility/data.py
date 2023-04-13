import pandas as pd
import numpy as np

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
