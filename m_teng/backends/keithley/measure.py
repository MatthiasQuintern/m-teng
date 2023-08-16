from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import pyvisa

from m_teng.backends.keithley.keithley import reset
from m_teng.utility import testing as _testing

def measure_count(instr, count=100, interval=0.05, update_func=None, update_interval=0.5, beep_done=True, verbose=True):
    """
    Take <count> measurements with <interval> inbetween

    @details
        Uses the devices overlappedY function to make the measurements asynchronosly
        The update_func is optional and only used when I == True and V == True
        The update_func does not necessarily get all the values that are measured. To obtain the whole measurement, get them from the device buffers (smua.nvbufferX)
    @param instr: pyvisa instrument
    @param update_func: Callable that processes the measurements: (index, ival, vval) -> None
    @param update_interval: interval at which the update_func is called
    """
    f_meas = "smua.measure.overlappediv(smua.nvbuffer1, smua.nvbuffer2)"
    # if V and I:
    # elif V:
    #     f_meas = "smua.measure.overlappedv(smua.nvbuffer1)"
    # elif I:
    #     f_meas = "smua.measure.overlappedi(smua.nvbuffer1)"
    # else:
    #     print("I and/or V needs to be set to True")
    #     return

    i = 0
    reset(instr, verbose=verbose)
    instr.write(f"smua.measure.count = {count}")
    instr.write(f"smua.measure.interval = {interval}")

    # start measurement
    instr.write(f"smua.source.output = smua.OUTPUT_ON")
    instr.write(f_meas)

    sleep(update_interval)
    # for live viewing
    query = """if smua.nvbufferX.n > 0 then print(smua.nvbufferX.readings[smua.nvbufferX.n]) else print(0) end"""

    # will return 2.0 while measruing
    while float(instr.query("print(status.operation.measuring.condition)").strip("\n ")) != 0:
        if update_func:
            try:
                ival = float(instr.query(query.replace("X", "1")).strip("\n"))
                vval = float(instr.query(query.replace("X", "2")).strip("\n"))
                update_func(i, ival, vval)
            except ValueError as e:
                if i != 0:
                    pass
                else:
                    print(f"measure_count: ValueError: {e}")
        sleep(update_interval)
        i += 1

    instr.write(f"smua.source.output = smua.OUTPUT_OFF")

    if beep_done:
        instr.write("beeper.beep(0.3, 1000)")


def measure(instr, interval, update_func=None, max_measurements=None):
    """
    @details:
        - Resets the buffers
        - Until KeyboardInterrupt:
            - Take measurement
            - Call update_func
            - Wait interval
        Uses python's time.sleep() for waiting the interval, which is not very precise. Use measure_count for better precision
        You can take the data from the buffer afterwards, using save_csv
    @param instr: pyvisa instrument
    @param update_func: Callable that processes the measurements: (index, ival, vval) -> None
    @param max_measurements : maximum number of measurements. None means infinite
    """
    reset(instr, verbose=True)
    instr.write("smua.source.output = smua.OUTPUT_ON")
    instr.write("format.data = format.ASCII\nformat.asciiprecision = 12")
    try:
        i = 0
        while max_measurements is None or i < max_measurements:
            ival, vval = tuple(float(v) for v in instr.query("print(smua.measure.iv(smua.nvbuffer1, smua.nvbuffer2))").strip('\n').split('\t'))
            if update_func:
                update_func(i, ival, vval)
            sleep(interval)
            i += 1
    except KeyboardInterrupt:
        pass
    instr.write("smua.source.output = smua.OUTPUT_OFF")
    print("Measurement stopped" + " "*50)
