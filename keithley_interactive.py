

"""
run this before using this library:
ipython -i keithley_interactive.py
"""

import numpy as np
import matplotlib.pyplot as plt
from sys import exit

settings = {
    "filename":     "measurement",
    "interval":     0.01,
    "beep":         True,
}

# global variable for the instrument returned by pyvisa
k = None


def measure():
    global k, settings
    pass

def monitor():
    """
    Monitor the voltage with matplotlib.

    @details:
        - Resets the buffers
        - Opens a matplotlib window and takes measurements depending on settings["interval"]
        - Waits for the user to press a key
    You can take the data from the buffer afterwards, using TODO
    """
    data = []
    for _ in range(1000):
        # data.append(tuple(float(v) for v in instr.query("print(smua.measure.v())").strip('\n').split('\t')))
        data.append(np.random())
        # print(i, data[-1])
        # clear_output(wait=True)
        plt.plot(data)
        plt.show()
        sleep(settings["interval"])
    pass

def save_csv():
    global k, settings
    """
    Saves the contents of nvbuffer1 as csv
    """
    pass

def help():
    print("""

          """)

def init():
    global k, settings
    print("""Interactive Keithley-Shell for TENG measurements.
Version 1.0
---
Enter 'help()' for a list of commands""")
    from keithley import init_keithley
    try:
        k = init_keithley(beep_success=settings["beep"])
    except Exception as e:
        print(e)
        exit()
