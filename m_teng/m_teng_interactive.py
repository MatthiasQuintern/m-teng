"""
run this before using this library:
ipython -i m_teng_interactive.py

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
import atexit

import argparse


if __name__ == "__main__":
    import sys
    if __package__ is None:
        # make relative imports work as described here: https://peps.python.org/pep-0366/#proposed-change
        __package__ = "m_teng"
        from os import path
        filepath = path.realpath(path.abspath(__file__))
        sys.path.insert(0, path.dirname(path.dirname(filepath)))
    parser = argparse.ArgumentParser(
        prog="m-teng",
        description="measure triboelectric nanogenerator output using a Keithley SMU or an Arduino",
    )
    backend_group = parser.add_mutually_exclusive_group(required=True)
    backend_group.add_argument("-k", "--keithley", action="store_true")
    backend_group.add_argument("-a", "--arduino", action="store_true")
    backend_group.add_argument("-t", "--testing", action='store_true')
    parser.add_argument("-c", "--config", action="store", help="alternate path to config file")
    args = vars(parser.parse_args())

    i = 1
    while i < len(sys.argv):
        if args["keithley"]:
            import m_teng.backends.keithley.keithley as _backend
            import m_teng.backends.keithley.measure as _measure
        elif args["arduino"]:
            import m_teng.backends.arduino.arduino as _backend
            import m_teng.backends.arduino.measure as _measure
        elif args["testing"]:
            import m_teng.backends.testing.testing as _backend
            import m_teng.backends.testing.measure as _measure
        elif sys.argv[i] in ["-c", "--config"]:
            if i+1 < len(sys.argv):
                config_path = sys.argv[i+1]
            else:
                print("-c requires an extra argument: path of config file")
            i += 1
        i += 1


from m_teng.utility import data as _data
from m_teng.utility.data import load_dataframe
from m_teng.utility import file_io
from m_teng.update_funcs import _Monitor, _ModelPredict, _update_print

config_path = path.expanduser("~/.config/k-teng.json")

_runtime_vars = {
    "last-measurement": ""
}

settings = {
    "datadir":      path.expanduser("~/data"),
    "name":         "measurement",
    "interval":     0.05,
    "beep":         True,
}

test = False

# global variable for the instrument/client returned by pyvisa/bleak
dev = None


def monitor_predict(model_dir: str, count=5000, interval=None, max_points_shown=160):
    """
    Take <count> measurements in <interval> and predict with a machine learning model
    """
    if not interval: interval = settings["interval"]

    model_predict = _ModelPredict(dev, model_dir)
    plt_monitor = _Monitor(max_points_shown, use_print=False)
    skip_n = 0
    def update(i, ival, vval):
        plt_monitor.update(i, ival, vval)
        if skip_n % 10 == 0:
            model_predict.update(i, ival, vval)
        skip_n += 1

    print(f"Starting measurement with:\n\tinterval = {interval}s\nSave the data using 'save_csv()' afterwards.")
    try:
        _measure.measure_count(dev, count=count, interval=interval, beep_done=False, verbose=False, update_func=update, update_interval=0.1)
    except KeyboardInterrupt:
        if args["keithley"]:
            dev.write(f"smua.source.output = smua.OUTPUT_OFF")
        print("Monitoring cancelled, measurement might still continue" + " "*50)
    else:
        print("Measurement finished" + " "*50)

def monitor_count(count=5000, interval=None, max_points_shown=160):
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
    if not interval: interval = settings["interval"]
    plt_monitor = _Monitor(max_points_shown, use_print=True)
    update_func = plt_monitor.update

    print(f"Starting measurement with:\n\tinterval = {interval}s\nSave the data using 'save_csv()' afterwards.")
    try:
        _measure.measure_count(dev, count=count, interval=interval, beep_done=False, verbose=False, update_func=update_func, update_interval=0.05)
    except KeyboardInterrupt:
        if args["keithley"]:
            dev.write(f"smua.source.output = smua.OUTPUT_OFF")
        print("Monitoring cancelled, measurement might still continue" + " "*50)
    else:
        print("Measurement finished" + " "*50)

def measure_count(count=5000, interval=None):
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
    if not interval: interval = settings["interval"]
    update_func = _update_print

    print(f"Starting measurement with:\n\tinterval = {interval}s\nSave the data using 'save_csv()' afterwards.")
    try:
        _measure.measure_count(dev, count=count, interval=interval, beep_done=False, verbose=False, update_func=update_func, update_interval=0.05)
    except KeyboardInterrupt:
        if args["keithley"]:
            dev.write(f"smua.source.output = smua.OUTPUT_OFF")
        print("Monitoring cancelled, measurement might still continue" + " "*50)
    else:
        print("Measurement finished" + " "*50)




def monitor(interval=None, max_measurements=None, max_points_shown=160):
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
    if not interval: interval = settings["interval"]
    print(f"Starting measurement with:\n\tinterval = {interval}s\nUse <C-c> to stop. Save the data using 'save_csv()' afterwards.")
    plt_monitor = _Monitor(use_print=True, max_points_shown=max_points_shown)
    update_func = plt_monitor.update
    _measure.measure(dev, interval=interval, max_measurements=max_measurements, update_func=update_func)


def measure(interval=None, max_measurements=None):
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
    if not interval: interval = settings["interval"]
    _runtime_vars["last_measurement"] = dtime.now().isoformat()
    print(f"Starting measurement with:\n\tinterval = {interval}s\nUse <C-c> to stop. Save the data using 'save_csv()' afterwards.")
    update_func = _update_print
    _measure.measure(dev, interval=interval, max_measurements=max_measurements, update_func=update_func)


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
    if settings["beep"]: _backend.beep()


def get_dataframe():
    """
    Get a pandas dataframe from the data in smua.nvbuffer1 and smua.nvbuffer2
    """
    global k, settings, _runtime_vars
    ibuffer = _backend.collect_buffer(dev, 1)
    vbuffer = _backend.collect_buffer(dev, 2)
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
        _keithley.run_lua(dev, script_path=script_path)


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
    measure         [kat] - take measurements
    monitor         [kat] - take measurements with live monitoring in a matplotlib window
    measure_count   [kat] - take a fixed number of measurements
    monitor_count   [kat] - take a fixed number of measurements with live monitoring in a matplotlib window
    repeat          [kat] - measure and save to csv multiple times
    get_dataframe   [kat] - return device internal buffer as pandas dataframe
    save_csv        [kat] - save the last measurement as csv file
    save_pickle     [kat] - save the last measurement as pickled pandas dataframe
    load_dataframe  [kat] - load a pandas dataframe from csv or pickle
    run_script      [k  ] - run a lua script on the Keithely device
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
    save_settings()        - store the settings as "m-teng.json" in the working directory
    load_settings()        - load settings from a file
    The global variable 'config_path' determines the path used by save/load_settings. Use -c '<path>' to set another path.
    The serach path is:
        <working-dir>/m-teng.json
        $XDG_CONFIG_HOME/m-teng.json
        ~/.config/m-teng.json
              """)
    elif topic == "imports":
        print("""Imports:
    numpy as np
    pandas as pd
    matplotlib.pyplot as plt
    os.path """)
    elif topic == "device":
        print("""Device:
    keithley backend:
        The opened pyvisa resource (deveithley device) is the global variable 'dev'.
        You can interact using pyvisa functions, such as
        k.write("command"), k.query("command") etc. to interact with the device.
    arduino backend:
        The Arduino will be avaiable as BleakClient using the global variable 'dev'.  """)
    else:
        print(topic.__doc__)


def init():
    global dev, settings, config_path
    print(r"""              ______________________ _______     ________
  _____       \__    ___/\_   _____/ \      \   /  _____/
 /     \  ______|    |    |    __)_  /   |   \ /   \  ___
|  Y Y  \/_____/|    |    |        \/    |    \\    \_\  \
|__|_|  /       |____|   /_______  /\____|__  / \______  /
      \/                         \/         \/         \/   1.2
Interactive Shell for TENG measurements with Keithley 2600B
---
Enter 'help()' for a list of commands""")
    from os import environ
    if path.isfile("m-teng.json"):
        config_path = "m-teng.json"
    elif 'XDG_CONFIG_HOME' in environ.keys():
        # and path.isfile(environ["XDG_CONFIG_HOME"] + "/m-teng.json"):
        config_path = environ["XDG_CONFIG_HOME"] + "/m-teng.json"
    else:
        config_path = path.expanduser("~/.config/m-teng.json")
    if args["config"]:
        config_path = args["config"]


    if not path.isdir(path.dirname(config_path)):
        makedirs(path.dirname(config_path))

    if path.isfile(config_path):
        load_settings()

    if not path.isdir(settings["datadir"]):
        makedirs(settings["datadir"])

    try:
        dev = _backend.init(beep_success=settings["beep"])
    except Exception as e:
        print(e)
        exit(1)
    atexit.register(_backend.exit, dev)


if __name__ == "__main__":
    init()
