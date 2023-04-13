import pyvisa
import numpy as np


"""
Utility
"""
script_dir = "scripts/"
scripts = {
    "buffer_reset":     "buffer_reset.lua",
    "smua_reset":       "smua_reset.lua",
}
for key,val in scripts.items():
    scripts[key] = script_dir + scripts[key]



def init_keithley(beep_success=True):
    rm = pyvisa.ResourceManager('@py')
    resources = rm.list_resources()
    if len(resources) < 1:
        raise Exception("No resources found.")
    elif len(resources) == 1:
        print(f"Opening Resource {resources[0]}")
        keithley = rm.open_resource(resources[0])
        if beep_success: keithley.write("beeper.beep(0.5, 1000)")
        return keithley
    elif len(resources) > 1:
        print(f"Resources: {resources}")
        instr = int(input("Select an instrument (0-based index)"))
        keithley = rm.open_resource(resources[instr])
        if beep_success: keithley.write("beeper.beep(0.5, 1000)")
        return keithley


def run_lua(instr, script_path, verbose=False):
    """
    Run a lua script from the host on the instrument
    @param instr : pyvisa instrument
    @param script_path : full path to the script
    """
    with open(script_path, "r") as file:
        script = file.read()
    if verbose: print(f"Running script: {script_path}")
    instr.write(script)


def reset(instr, verbose=False):
    """
    Reset smua and its buffers
    @param instr : pyvisa instrument
    """
    run_lua(instr, scripts["smua_reset"], verbose=verbose)
    run_lua(instr, scripts["buffer_reset"], verbose=verbose)


def collect_buffer(instr, buffer_nr=1):
    """
    Get the buffer as 2D - np.array
    @param instr : pyvisa instrument
    @param buffer_nr : 1 or 2, for smua.nvbuffer1 or 2
    @returns 2D numpy array:
        i - ith reading:
            0: timestamps
            1: readings
    """
    if buffer_nr == 2: buffername = "smua.nvbuffer2"
    else: buffername = "smua.nvbuffer1"
    # instr.write("format.data = format.DREAL\nformat.byteorder = format.LITTLEENDIAN")
    # buffer = instr.query_binary_values(f"printbuffer(1, {buffername}.n, {buffername})", datatype='d', container=np.array)
    instr.write("format.data = format.ASCII\nformat.asciiprecision = 7")
    timestamps = instr.query_ascii_values(f"printbuffer(1, {buffername}.n, {buffername}.timestamps)", container=np.array)
    readings = instr.query_ascii_values(f"printbuffer(1, {buffername}.n, {buffername}.readings)", container=np.array)
    print(f"readings: {readings}, \ntimestamps: {timestamps}")
    buffer = np.vstack((timestamps, readings)).T
    return buffer

