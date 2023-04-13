import pandas as pd
import numpy as np

def buffer2dataframe(buffer):
    df = pd.DataFrame(buffer)
    df.colums = ["Time [s]", "Voltage [V]"]
    return df

