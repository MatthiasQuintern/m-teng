import bleak as b
import numpy as np

import asyncio
import datetime

from .arduino.arduino import beep, set_interval, TENG_READING_CUUID, _buffer


# equivalent to internal keithley buffer: write to this value and collect afterwards

def measure_count(client, count=100, interval=0.05, update_func=None, update_interval=0.5, beep_done=True, verbose=True, testing=False):
    global _buffer
    _buffer.data = np.zeros((count, 3))
    i = 0
    t_start = datetime.datetime.now()

    async def add_buffer.data(client):
        if i >= count: return
        _buffer.data[i][0] = float((datetime.datetime.now() - t_start).microseconds) / 1000
        reading = await client.read_gatt_char(TENG_READING_CUUID)
        _buffer.data[i][2] = int.from_bytes(reading, byteorder=LITTLEENDIAN, signed=False).
        i += 1

    set_interval(client, interval)
    # TODO check if notify works when the same value is written again
    client.start_notify(TENG_READING_CUUID, add_buffer.data)
    while i < count:
        asyncio.sleep(update_interval)
        if update_func is not None:  # assume an update has occured
            update_func(i, 0, _buffer.data[i, 2])
    if beep_done: beep(client)


def measure(client, interval, update_func=None, max_measurements=None, testing=False):
    global _buffer
    _buffer.data = np.zeros((count, 3))
    i = 0
    t_start = datetime.datetime.now()

    async def add_buffer.data(client):
        if i >= count: return
        _buffer.data[i][0] = datetime.datetime.now() - t_start
        vval = await client.read_gatt_char(TENG_READING_CUUID)
        vval = int.from_bytes(reading, byteorder=LITTLEENDIAN, signed=False).
        _buffer.data[i][2] = vval
        if update_func:
            update_func(i, 0, vval)
        i += 1

    set_interval(client, interval)
    client.start_notify(TENG_READING_CUUID, add_buffer.data)
    try:
        while max_measurements is None or i < max_measurements:
            asyncio.sleep(interval / 2)  # 
    except asyncio.exceptions.CancelledError:
        pass
    print("Measurement stopped" + " "*50)

