import pyvisa
import numpy as np
import pkg_resources


"""
Utility
"""

scripts = {
    "buffer_reset": pkg_resources.resource_filename("m_teng", "keithley_scripts/buffer_reset.lua"),
    "smua_reset":   pkg_resources.resource_filename("m_teng", "keithley_scripts/smua_reset.lua"),
}


def init(beep_success=True):
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


def exit(instr):
    instr.close()



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

def get_buffer_name(buffer_nr: int):
    if buffer_nr == 2: return "smua.nvbuffer2"
    elif buffer_nr == 1:  return "smua.nvbuffer1"
    raise ValueError(f"Invalid buffer_nr: {buffer_nr}")

def get_buffer_size(instr, buffer_nr=1):
    n = instr.query(f"print({get_buffer_name(buffer_nr)}.n)").strip("\n")
    return int(float(n))


def collect_buffer(instr, buffer_nr=1, verbose=False):
    """
    Get the buffer as 2D - np.array
    @param instr : pyvisa instrument
    @param buffer_nr : 1 or 2, for smua.nvbuffer1 or 2
    @returns 2D numpy array:
        i - ith reading:
            0: timestamps
            1: readings
    """
    buffername = get_buffer_name(buffer_nr)
    # instr.write("format.data = format.DREAL\nformat.byteorder = format.LITTLEENDIAN")
    # buffer = instr.query_binary_values(f"printbuffer(1, {buffername}.n, {buffername})", datatype='d', container=np.array)
    instr.write("format.data = format.ASCII\nformat.asciiprecision = 7")
    timestamps = instr.query_ascii_values(f"printbuffer(1, {buffername}.n, {buffername}.timestamps)", container=np.array)
    readings = instr.query_ascii_values(f"printbuffer(1, {buffername}.n, {buffername}.readings)", container=np.array)
    if verbose:
        print(f"readings from {buffername}: {readings}, \ntimestamps: {timestamps}")
    buffer = np.vstack((timestamps, readings)).T
    return buffer



def collect_buffer_range(instr, range_=(1, -1), buffer_nr=1, verbose=False):
    """
    Get the buffer as 2D - np.array
    @param instr : pyvisa instrument
    @param buffer_nr : 1 or 2, for smua.nvbuffer1 or 2
    @returns 2D numpy array:
        i - ith reading:
            0: timestamps
            1: readings
    """
    buffername = get_buffer_name(buffer_nr)
    # instr.write("format.data = format.DREAL\nformat.byteorder = format.LITTLEENDIAN")
    # buffer = instr.query_binary_values(f"printbuffer(1, {buffername}.n, {buffername})", datatype='d', container=np.array)
    if range_[1] == -1:
        range_ = (range_[0], f"{buffername}.n")
    instr.write("format.data = format.ASCII\nformat.asciiprecision = 7")
    timestamps = instr.query_ascii_values(f"printbuffer({range_[0]}, {range_[1]}, {buffername}.timestamps)", container=np.array)
    readings = instr.query_ascii_values(f"printbuffer({range_[0]}, {range_[1]}, {buffername}.readings)", container=np.array)
    if verbose:
        print(f"readings from {buffername}: {readings}, \ntimestamps: {timestamps}")
    buffer = np.vstack((timestamps, readings)).T
    return buffer



