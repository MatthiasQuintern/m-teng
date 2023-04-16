"""
run this before using this library:
ipython -i keithley_interactive.py

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
from .utility import data as _data
from .utility.data import load_dataframe
from .utility import file_io
from .utility import testing

_runtime_vars = {
    "last-measurement": ""
}

settings = {
    "datadir":      path.expanduser("~/data"),
    "name":         "measurement",
    "interval":     0.01,
    "beep":         True,
}
config_path = path.expanduser("~/.config/k-teng.json")

test = False

# global variable for the instrument returned by pyvisa
k = None


def _measure(max_measurements=None, max_points_shown=None, monitor=False):
    """
    Monitor the voltage with matplotlib.

    @details:
        - Resets the buffers
        - Opens a matplotlib window and takes measurements depending on settings["interval"]
        - Waits for the user to press a key
    @param max_points_shown : how many points should be shown at once. None means infinite
    @param max_measurements : maximum number of measurements. None means infinite
    You can take the data from the buffer afterwards, using save_csv """
    global k, settings, test, _runtime_vars
    print(f"Starting measurement with:\n\tinterval = {settings['interval']}s\nUse <C-c> to stop. Save the data using 'save_csv()' afterwards.")
    _runtime_vars["last_measurement"] = dtime.now().isoformat()
    if not test:
        _keithley.reset(k, verbose=True)
        k.write("smua.source.output = 1")
        k.write("format.data = format.ASCII\nformat.asciiprecision = 12")
    # jupyter:
    # clear_output(wait=True)
    # plt.plot(data)
    # plt.show()
    index = []
    vdata = []
    idata = []
    if monitor:
        plt.ion()
        fig1, (vax, iax) = plt.subplots(2, 1)

        vline,  = vax.plot(index, vdata, color="g")
        vax.set_ylabel("Voltage [V]")
        vax.grid(True)

        iline,  = iax.plot(index, idata, color="m")
        iax.set_ylabel("Current [A]")
        iax.grid(True)
    try:
        i = 0
        while max_measurements is None or i < max_measurements:
            index.append(i)
            if test:
                idata.append(testing.testcurve(i, peak_width=1, amplitude=5e-8))
                vdata.append(-testing.testcurve(i, peak_width=2, amplitude=15))
                # data.append(np.random.rand())
            else:
                # data.append(float(k.query("print(smua.measure.v(smua.nvbuffer1))").strip('\n')))
                i_val, v_val = tuple(float(v) for v in k.query("print(smua.measure.iv(smua.nvbuffer1, smua.nvbuffer2))").strip('\n').split('\t'))
                idata.append(i_val)
                vdata.append(v_val)
            print(f"{i:5d} - {idata[-1]:.12f} A - {vdata[-1]:.5f} V", end='\r')
            if monitor:
                # update data
                iline.set_xdata(index)
                iline.set_ydata(idata)
                vline.set_xdata(index)
                vline.set_ydata(vdata)
                # recalculate limits and set them for the view
                iax.relim()
                vax.relim()
                if max_points_shown and i > max_points_shown:
                    iax.set_xlim(i - max_points_shown, i)
                    vax.set_xlim(i - max_points_shown, i)
                iax.autoscale_view()
                vax.autoscale_view()
                # update plot
                fig1.canvas.draw()
                fig1.canvas.flush_events()
            sleep(settings["interval"])
            i += 1
    except KeyboardInterrupt:
        if not test:
            k.write("smua.source.output = 0")
        if monitor:
            plt.close(fig1)
        print("Measurement stopped" + " "*50)
    return vdata, idata


def monitor(max_measurements=None, max_points_shown=160):
    """
    Monitor the voltage with matplotlib.

    @details:
        - Resets the buffers
        - Opens a matplotlib window and takes measurements depending on settings["interval"]
        - Waits for the user to press a key
    @param max_points_shown : how many points should be shown at once. None means infinite
    @param max_measurements : maximum number of measurements. None means infinite
    You can take the data from the buffer afterwards, using save_csv """
    _measure(max_measurements=max_measurements, max_points_shown=max_points_shown, monitor=True)


def measure(max_measurements=None):
    """
    Measure voltages

    @details:
        - Resets the buffers
        - Measure voltages
        - Waits for the user to press a key
    @param max_measurements : maximum number of measurements. None means infinite
    You can take the data from the buffer afterwards, using save_csv """
    _measure(max_measurements=max_measurements, monitor=False)

def automeasure(repeat, repeat_delay=0, max_measurements=None, max_points_shown=120, monitor=True):
    """
    Measure and save to csv multiple times
    """
    for i in range(repeat):
        _measure(max_measurements=max_measurements, max_points_shown=max_points_shown, monitor=monitor)
        save_csv()
        sleep(repeat_delay)


def get_dataframe():
    """
    Get a pandas dataframe from the data in smua.nvbuffer1
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
    settings["datadir"] = path.expanduser(settings["datadir"])

def help(topic=None):
    if topic == None:
        print("""
Functions:
    measure         - measure the voltage
    monitor         - measure the voltage with live monitoring in a matplotlib window
    automeasure     - measure and save to csv multiple times
    get_dataframe   - return smua.nvbuffer1 as pandas dataframe
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
        \/                            \/         \/         \/      1.0
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
