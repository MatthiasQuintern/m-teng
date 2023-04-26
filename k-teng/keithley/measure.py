from time import sleep
import numpy as np
from matplotlib import pyplot as plt
import pyvisa

from .keithley import reset
from ..utility import testing as _testing

def measure_count(instr, V=True, I=True, count=100, interval=0.05, update_func=None, update_interval=0.5, beep_done=True, verbose=True, testing=False):
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
    f_meas = None
    if V and I:
        f_meas = "smua.measure.overlappediv(smua.nvbuffer1, smua.nvbuffer2)"
    elif V:
        f_meas = "smua.measure.overlappedv(smua.nvbuffer1)"
    elif I:
        f_meas = "smua.measure.overlappedi(smua.nvbuffer1)"
    else:
        print("I and/or V needs to be set to True")
        return

    i = 0
    if not testing:
        reset(instr, verbose=verbose)
        instr.write(f"smua.measure.count = {count}")
        instr.write(f"smua.measure.interval = {interval}")

        # start measurement
        instr.write(f"smua.source.output = smua.OUTPUT_ON")
        instr.write(f_meas)

        condition = lambda: float(instr.query("print(status.operation.measuring.condition)").strip("\n ")) != 0
    else:
        condition = lambda: i < int(float(count) * interval / update_interval)

    sleep(update_interval)
    # for live viewing

    # will return 2.0 while measruing
    while condition():
        if update_func and V and I:
            try:
                if not testing:
                    ival = float(instr.query("print(smua.nvbuffer1.readings[smua.nvbuffer1.n])").strip("\n"))
                    vval = float(instr.query("print(smua.nvbuffer2.readings[smua.nvbuffer2.n])").strip("\n"))
                else:
                    ival = _testing.testcurve(i, peak_width=1, amplitude=5e-8)
                    vval = -_testing.testcurve(i, peak_width=2, amplitude=15)
                update_func(i, ival, vval)
            except ValueError:
                pass
        sleep(update_interval)
        i += 1

    if not testing:
        instr.write(f"smua.source.output = smua.OUTPUT_OFF")

        if beep_done:
            instr.write("beeper.beep(0.3, 1000)")


def measure(instr, interval, update_func=None, max_measurements=None, testing=False):
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
    if not testing:
        reset(instr, verbose=True)
        instr.write("smua.source.output = smua.OUTPUT_ON")
        instr.write("format.data = format.ASCII\nformat.asciiprecision = 12")
    try:
        i = 0
        while max_measurements is None or i < max_measurements:
            if testing:
                ival = _testing.testcurve(i, peak_width=1, amplitude=5e-8)
                vval = -_testing.testcurve(i, peak_width=2, amplitude=15)
            else:
                ival, vval = tuple(float(v) for v in instr.query("print(smua.measure.iv(smua.nvbuffer1, smua.nvbuffer2))").strip('\n').split('\t'))
            if update_func:
                update_func(i, ival, vval)
            sleep(interval)
            i += 1
    except KeyboardInterrupt:
        pass
    if not testing:
        instr.write("smua.source.output = smua.OUTPUT_OFF")
    print("Measurement stopped" + " "*50)
