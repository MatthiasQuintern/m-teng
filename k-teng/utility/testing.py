
import pandas as pd
import numpy as np

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


def testcurve(x, frequency=10, peak_width=2, amplitude=20, bias=0):
    # want peak at n*time == frequency
    nearest_peak = np.round(x / frequency, 0)
    # if not peak at 0 and within peak_width
    if nearest_peak > 0 and abs((x - nearest_peak * frequency)) < peak_width:
        # return sin that does one period within 2*peak_width
        return amplitude * np.sin(2*np.pi * (x - nearest_peak * frequency - peak_width) / (2*peak_width)) + bias
    else:
        return bias

    # 0 = pk - width
    # 2pi = pk + width
