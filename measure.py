from time import sleep
import numpy as np
from matplotlib import pyplot as plt

smua_settings = """
display.clear()
display.settext('starting')
smua.reset()
smua.measure.autorangev = smua.AUTORANGE_ON
smua.measure.autozero = smua.AUTOZERO_ONCE
smua.source.output = smua.OUTPUT_OFF
-- max 20 V expected
smua.measure.rangev = 20

"""

script_dir = "scripts/"

scripts = {
    "buffer_reset":     "buffer_reset.lua",
    "smua_reset":       "smua_reset.lua",
}


def run_lua(instr, script_path, verbose=False):
    with open(script_dir + script_path, "r") as file:
        script = file.read()
    if verbose: print(f"Running script: {script_dir + script_path}")
    instr.write(script)


def measure_V(instr, count=100, interval=0.05):
    """
    """
    data = []
    for _ in range(1000):
        data.append(tuple(float(v) for v in instr.query("print(smua.measure.v())").strip('\n').split('\t')))
        # print(i, data[-1])
        # clear_output(wait=True)
        plt.plot(data)
        plt.show()
        sleep(0.05)

def reset(instr):
    run_lua(instr, scripts["smua_reset"], verbose=verbose)
    run_lua(instr, scripts["buffer_reset"], verbose=verbose)


def measure_count(instr, V=True, I=True, count=100, interval=0.05, beep_done=True, verbose=True):
    """
    take n measurements at dt interval
    """
    reset(instr)
    f_meas = None
    if V and I:
        f_meas = "smua.measure.iv(smua.nvbuffer1, smua.nvbuffer2)"
    elif V:
        f_meas = "smua.measure.v(smua.nvbuffer1)"
    elif I:
        f_meas = "smua.measure.i(smua.nvbuffer1)"
    else:
        print("I and/or V needs to be set to True")
        return

    instr.write(f"smua.measure.count = {count}")
    instr.write(f"smua.measure.interval = {interval}")

    instr.write(f"smua.source.output = smua.OUTPUT_ON")
    instr.write(f_meas)
    instr.write(f"smua.source.output = smua.OUTPUT_OFF")

    if beep_done:
        instr.write("beeper.beep(0.3, 1000)")


def collect_buffer(instr, buffer_nr=1):
    """
    get the buffer as 2D - np.array
        i - ith reading
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



def event_test_TODO():
        # Type of event we want to be notified about
    event_type = pyvisa.constants.EventType.service_request
    # Mechanism by which we want to be notified
    event_mech = pyvisa.constants.EventMechanism.queue
    keithley.enable_event(event_type, event_mech)

    # Instrument specific code to enable service request
    # (for example on operation complete OPC)
    keithley.write("*SRE 1")
    keithley.write("INIT")


    with open("script.lua", "r") as file:
        script = file.read()
    # for line in script.split('\n'):
    #     input(line)
    #     keithley.write(line)
    keithley.write(script)

    # Wait for the event to occur
    response = keithley.wait_on_event(event_type, 1000)
    assert response.event.event_type == event_type
    assert response.timed_out == False

    instr.disable_event(event_type, event_mech)
    keithley.query_ascii_values("printbuffer(1, 10, smua.nvbuffer1)", 6)
    print(voltages)
