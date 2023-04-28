"""
run this before using this library:
ipython -i k_teng_interactive.py

always records iv-t curves
    i-data -> smua.nvbuffer1
    v-data -> smua.nvbuffer2
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from datetime import datetime as dtime
from sys import exit
from time import sleep
from os import path, makedirs
import pickle as pkl
import json

if __name__ == "__main__":
    if __package__ is None:
        # make relative imports work as described here: https://peps.python.org/pep-0366/#proposed-change
        __package__ = "k-teng"
        import sys
        from os import path
        filepath = path.realpath(path.abspath(__file__))
        sys.path.insert(0, path.dirname(path.dirname(filepath)))


from .keithley import keithley as _keithley
from .keithley.measure import measure_count as _measure_count, measure as _measure
from .utility import data as _data
from .utility.data import load_dataframe
from .utility import file_io

_runtime_vars = {
    "last-measurement": ""
}

settings = {
    "datadir":      path.expanduser("~/data"),
    "name":         "measurement",
    "interval":     0.02,
    "beep":         True,
}
config_path = path.expanduser("~/.config/k-teng.json")

test = False

# global variable for the instrument returned by pyvisa
k = None



def _update_print(i, ival, vval):
    print(f"n = {i:5d}, I = {ival: .12f} A, U = {vval: .5f} V" + " "*10, end='\r')

class _Monitor:
    """
    Monitor v and i data
    """
    def __init__(self, max_points_shown=None, use_print=False):
        self.max_points_shown = max_points_shown
        self.use_print = use_print
        self.index = []
        self.vdata = []
        self.idata = []

        plt.ion()
        self.fig1, (self.vax, self.iax) = plt.subplots(2, 1, figsize=(8, 5))

        self.vline,  = self.vax.plot(self.index, self.vdata, color="g")
        self.vax.set_ylabel("Voltage [V]")
        self.vax.grid(True)

        self.iline,  = self.iax.plot(self.index, self.idata, color="m")
        self.iax.set_ylabel("Current [A]")
        self.iax.grid(True)

    def update(self, i, ival, vval):
        if self.use_print:
            _update_print(i, ival, vval)
        self.index.append(i)
        self.idata.append(ival)
        self.vdata.append(vval)
        # update data
        self.iline.set_xdata(self.index)
        self.iline.set_ydata(self.idata)
        self.vline.set_xdata(self.index)
        self.vline.set_ydata(self.vdata)
        # recalculate limits and set them for the view
        self.iax.relim()
        self.vax.relim()
        if self.max_points_shown and i > self.max_points_shown:
            self.iax.set_xlim(i - self.max_points_shown, i)
            self.vax.set_xlim(i - self.max_points_shown, i)
        self.iax.autoscale_view()
        self.vax.autoscale_view()
        # update plot
        self.fig1.canvas.draw()
        self.fig1.canvas.flush_events()

    def __del__(self):
        plt.close(self.fig1)


def monitor_count(count=5000, interval=settings["interval"], max_points_shown=160):
    """
    Take <count> measurements in <interval> and monitor live with matplotlib.

    @details:
        - Resets the buffers
        - Opens a matplotlib window and takes measurements depending on settings["interval"]
        Uses the device internal overlappedY measurement method, which allows for greater precision
        You can take the data from the buffer afterwards, using save_csv
    @param count: count
    @param interval: interval, defaults to settings["interval"]
    @param max_points_shown: how many points should be shown at once. None means infinite
    """
    plt_monitor = _Monitor(max_points_shown, use_print=True)
    update_func = plt_monitor.update

    print(f"Starting measurement with:\n\tinterval = {interval}s\nSave the data using 'save_csv()' afterwards.")
    try:
        _measure_count(k, V=True, I=True, count=count, interval=interval, beep_done=False, verbose=False, update_func=update_func, update_interval=0.05, testing=test)
    except KeyboardInterrupt:
        if not test:
            k.write(f"smua.source.output = smua.OUTPUT_OFF")
        print("Monitoring cancelled, measurement might still continue" + " "*50)
    else:
        print("Measurement finished" + " "*50)

def measure_count(count=5000, interval=settings["interval"]):
    """
    Take <count> measurements in <interval>

    @details:
        - Resets the buffers
        - Takes <count> measurements depending on settings["interval"]
        Uses the device internal overlappedY measurement method, which allows for greater precision
        You can take the data from the buffer afterwards, using save_csv
    @param count: count
    @param interval: interval, defaults to settings["interval"]
    """
    update_func = _update_print

    print(f"Starting measurement with:\n\tinterval = {interval}s\nSave the data using 'save_csv()' afterwards.")
    try:
        _measure_count(k, V=True, I=True, count=count, interval=interval, beep_done=False, verbose=False, update_func=update_func, update_interval=0.05, testing=test)
    except KeyboardInterrupt:
        if not test:
            k.write(f"smua.source.output = smua.OUTPUT_OFF")
        print("Monitoring cancelled, measurement might still continue" + " "*50)
    else:
        print("Measurement finished" + " "*50)




def monitor(interval=settings["interval"], max_measurements=None, max_points_shown=160):
    """
    Monitor the voltage with matplotlib.

    @details:
        - Resets the buffers
        - Opens a matplotlib window and takes measurements depending on settings["interval"]
        - Waits for the user to press a key
        Uses python's time.sleep() for waiting the interval, which is not very precise. Use measure_count for better precision.
        You can take the data from the buffer afterwards, using save_csv.
    @param max_points_shown : how many points should be shown at once. None means infinite
    @param max_measurements : maximum number of measurements. None means infinite
    """
    global _runtime_vars
    _runtime_vars["last_measurement"] = dtime.now().isoformat()
    print(f"Starting measurement with:\n\tinterval = {interval}s\nUse <C-c> to stop. Save the data using 'save_csv()' afterwards.")
    plt_monitor = _Monitor(use_print=True, max_points_shown=max_points_shown)
    update_func = plt_monitor.update
    _measure(k, interval=interval, max_measurements=max_measurements, update_func=update_func, testing=test)


def measure(interval=settings["interval"], max_measurements=None):
    """
    Measure voltages

    @details:
        - Resets the buffers
        - Measure voltages
        - Waits for the user to press a key
        Uses python's time.sleep() for waiting the interval, which is not very precise. Use measure_count for better precision.
        You can take the data from the buffer afterwards, using save_csv.
    @param max_measurements : maximum number of measurements. None means infinite
    """
    global _runtime_vars
    _runtime_vars["last_measurement"] = dtime.now().isoformat()
    print(f"Starting measurement with:\n\tinterval = {interval}s\nUse <C-c> to stop. Save the data using 'save_csv()' afterwards.")
    update_func = _update_print
    _measure(k, interval=interval, max_measurements=max_measurements, update_func=update_func, testing=test)


def repeat(measure_func: callable, count: int, repeat_delay=0):
    """
    Measure and save to csv multiple times

    @details
        Repeat count times:
        - call measure_func
        - call save_csv
        - sleep for repeat_delay

    @param measure_func: The measurement function to use. Use a lambda to bind your parameters!
    @param count: Repeat count times

    Example: Repeat 10 times:
        repeat(lambda : monitor_count(count=6000, interval=0.02, max_points_shown=200), 10)
    """
    try:
        for _ in range(count):
            measure_func()
            save_csv()
            sleep(repeat_delay)
    except KeyboardInterrupt:
        pass
    if settings["beep"]: k.write("beeper.beep(0.3, 1000)")


def get_dataframe():
    """
    Get a pandas dataframe from the data in smua.nvbuffer1 and smua.nvbuffer2
    """
    global k, settings, _runtime_vars
    if test:
        timestamps = np.arange(0, 50, 0.01)
        ydata = np.array([testing.testcurve(t, amplitude=15, peak_width=2) for t in timestamps])
        ibuffer = np.vstack((timestamps, ydata)).T

        ydata = np.array([-testing.testcurve(t, amplitude=5e-8, peak_width=1) for t in timestamps])
        vbuffer = np.vstack((timestamps, ydata)).T
    else:
        ibuffer = _keithley.collect_buffer(k, 1)
        vbuffer = _keithley.collect_buffer(k, 2)
    df = _data.buffers2dataframe(ibuffer, vbuffer)
    df.basename = file_io.get_next_filename(settings["name"], settings["datadir"])
    df.name = f"{df.basename} @ {_runtime_vars['last-measurement']}"
    return df

def save_csv():
    """
    Saves the contents of nvbuffer1 as .csv
    The settings 'datadir' and 'name' are used for determining the filepath:
    'datadir/nameXXX.csv', where XXX is the number of files that exist in datadir with the same name.
    """
    df = get_dataframe()
    filename = settings["datadir"] + "/" + df.basename + ".csv"
    df.to_csv(filename, index=False, header=True)
    print(f"Saved as '{filename}'")


def save_pickle():
    """
    Saves the contents of nvbuffer1 as .pkl
    The settings 'datadir' and 'name' are used for determining the filepath:
    'datadir/nameXXX.pkl', where XXX is the number of files that exist in datadir with the same name.
    """
    df = get_dataframe()
    filename = settings["datadir"] + "/" + df.basename + ".pkl"
    df.to_pickle(filename)
    print(f"Saved as '{filename}'")

def run_script(script_path):
    """
    Run a lua script on the Keithley device
    @param script_path : relative or absolute path to the .lua script
    """
    global k, settings
    if test:
        print("run_script: Test mode enabled, ignoring call to run_script")
    else:
        _keithley.run_lua(k, script_path=script_path)


def set(setting, value):
    global settings, config_path
    if setting in settings:
        if type(value) != type(settings[setting]):
            print(f"set: setting '{setting}' currently holds a value of type '{type(settings[setting])}'")
            return
    settings[setting] = value

def name(s:str):
    global settings
    settings["name"] = s

def save_settings():
    with open(config_path, "w") as file:
        json.dump(settings, file, indent=4)

def load_settings():
    global settings, config_path
    with open(config_path, "r") as file:
        settings = json.load(file)
    settings["datadir"] = path.expanduser(settings["datadir"])  # replace ~

def help(topic=None):
    if topic == None:
        print("""
Functions:
    measure         - take measurements
    monitor         - take measurements with live monitoring in a matplotlib window
    measure_count   - take a fixed number of measurements
    monitor_count   - take a fixed number of measurements with live monitoring in a matplotlib window
    repeat          - measure and save to csv multiple times
    get_dataframe   - return smua.nvbuffer 1 and 2 as pandas dataframe
    save_csv        - save the last measurement as csv file
    save_pickle     - save the last measurement as pickled pandas dataframe
    load_dataframe  - load a pandas dataframe from csv or pickle
    run_script      - run a lua script on the Keithely device
Run 'help(function)' to see more information on a function

Available topics:
    imports
    device
    settings
Run 'help("topic")' to see more information on a topic""")

    elif topic in [settings, "settings"]:
        print("""Settings:
    name: str       - name of the measurement, determines filename of 'save_csv'
    datadir: str    - output directory for the csv files
    interval: int   - interval (inverse frequency) of the measurements, in seconds
    beep: bool      - wether the device should beep or not

Functions:
    name("<name>")         - short for set("name", "<name>")
    set("setting", value)  - set a setting to a value
    save_settings()        - store the settings as "k-teng.conf" in the working directory
    load_settings()        - load settings from a file
    The global variable 'config_path' determines the path used by save/load_settings. Use -c '<path>' to set another path.
    The serach path is:
        <working-dir>/k-teng.json
        $XDG_CONFIG_HOME/k-teng.json
        ~/.config/k-teng.json
              """)
    elif topic == "imports":
        print("""Imports:
    numpy as np
    pandas as pd
    matplotlib.pyplot as plt
    os.path """)
    elif topic == "device":
        print("""Device:
    The opened pyvisa resource (Keithley device) is the global variable 'k'.
    You can interact using pyvisa functions, such as
    k.write("command"), k.query("command") etc. to interact with the device.""")
    else:
        print(topic.__doc__)


def init():
    global k, settings, test, config_path
    print(r""" ____  __.         ______________________ _______     ________
|    |/ _|         \__    ___/\_   _____/ \      \   /  _____/
|      <    ______   |    |    |    __)_  /   |   \ /   \  ___
|    |  \  /_____/   |    |    |        \/    |    \\    \_\  \
|____|__ \           |____|   /_______  /\____|__  / \______  /
        \/                            \/         \/         \/      1.1
Interactive Shell for TENG measurements with Keithley 2600B
---
Enter 'help()' for a list of commands""")
    from os import environ
    if path.isfile("k-teng.json"):
        config_path = "k-teng.json"
    elif 'XDG_CONFIG_HOME' in environ.keys():
        # and path.isfile(environ["XDG_CONFIG_HOME"] + "/k-teng.json"):
        config_path = environ["XDG_CONFIG_HOME"] + "/k-teng.json"
    else:
        config_path = path.expanduser("~/.config/k-teng.json")

    from sys import argv
    i = 1
    while i < len(argv):
        if argv[i] in ["-t", "--test"]:
            test = True
        elif argv[i] in ["-c", "--config"]:
            if i+1 < len(argv):
                config_path = argv[i+1]
            else:
                print("-c requires an extra argument: path of config file")
            i += 1
        i += 1


    if not path.isdir(path.dirname(config_path)):
        makedirs(path.dirname(config_path))

    if path.isfile(config_path):
        load_settings()

    if not path.isdir(settings["datadir"]):
        makedirs(settings["datadir"])

    if not test:
        from .keithley.keithley import init_keithley
        try:
            k = init_keithley(beep_success=settings["beep"])
        except Exception as e:
            print(e)
            exit()
    else:
        print("Running in test mode, device will not be connected.")


if __name__ == "__main__":
    init()
