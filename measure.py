from time import sleep
import numpy as np
from matplotlib import pyplot as plt

smua_settings = """
display.clear()
display.settext('starting')
smua.reset()
smua.measure.autorangev = smua.AUTORANGE_ON
smua.source.output = smua.OUTPUT_OFF
-- max 20 V expected
smua.measure.rangev = 20

"""

script_dir = ""

scripts = {
    "buffer_reset": "scripts/buffer_reset.lua",
}

def run_lua(instr, script_path):
    with open(script_dir + script_path, "r") as file:
        script = file.read()
    instr.write(script)


def measureV(count=100, interval=0.05)
    """
    """
    data = []
    for i in range(1000):
        data.append(tuple(float(v) for v in keithley.query("print(smua.measure.v())").strip('\n').split('\t')))
        # print(i, data[-1])
        # clear_output(wait=True)
        plt.plot(data)
        plt.show()
        sleep(0.05)

def collect_buffer(instr, buffer_nr=1):
    """
    get the buffer in double precision binary format as np.array
    """
    if buffer_nr == 2: buffername = "smua.nvbuffer2"
    else: buffername = "smua.nvbuffer1"
    instr.write("format.data = format.DREAL\nformat.byteorder = format.LITTLEENDIAN")
    buffer = instr.query_ascii_values(f"printbuffer(1, {buffername}.n, {buffername})", datatype='d', container=np.array)
    return buffer
