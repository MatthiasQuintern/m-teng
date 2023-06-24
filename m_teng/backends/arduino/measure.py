import bleak as b
import numpy as np

import asyncio
import datetime

from m_teng.backends.arduino.arduino import beep, set_interval, set_count, TENG_READING_CUUID, _buffer, start_measure, start_measure_count, stop_measurement, runner


async def _measure_count_async(client, count=100, interval=0.05, update_func=None, update_interval=0.5, beep_done=True, verbose=True):
    global _buffer
    _buffer.data = np.zeros((count, 3))
    i = 0
    t_start = datetime.datetime.now()
    async def add_reading(teng_reading_cr, reading: bytearray):
        nonlocal i, count
        if i >= count: return
        _buffer.data[i][0] = float((datetime.datetime.now() - t_start).microseconds) / 1000
        # reading = await client.read_gatt_char(TENG_READING_CUUID)
        _buffer.data[i][2] = int.from_bytes(reading, byteorder="little", signed=False)
        i += 1

    await set_interval(client, interval)
    await set_count(client, count)
    # TODO check if notify works when the same value is written again
    await client.start_notify(TENG_READING_CUUID, add_reading)
    await start_measure_count(client)
    while i < count:
        await asyncio.sleep(update_interval)
        if update_func is not None and i > 0:  # assume an update has occured
            update_func(i-1, 0, _buffer.data[i-1, 2])
    await client.stop_notify(TENG_READING_CUUID)
    if beep_done: beep(client)

def measure_count(client, count=100, interval=0.05, update_func=None, update_interval=0.5, beep_done=True, verbose=True):
    runner.run(_measure_count_async(client, count=count, interval=interval, update_func=update_func, update_interval=update_interval, beep_done=beep_done, verbose=verbose))


async def _measure_async(client, interval, update_func=None, max_measurements=None):
    global _buffer
    readings = []
    timestamps = []
    i = 0
    t_start = datetime.datetime.now()

    async def add_reading(teng_reading_cr, reading):
        nonlocal i
        timestamps.append(float((datetime.datetime.now() - t_start).microseconds) / 1000)
        reading = int.from_bytes(reading, byteorder="little", signed=False)
        readings.append(reading)

        if update_func:
            try:
                update_func(i, 0, reading)
            except KeyboardInterrupt:
                raise asyncio.exceptions.CancelledError("KeyboardInterrupt in update_func")
        i += 1

    await set_interval(client, interval)
    await client.start_notify(TENG_READING_CUUID, add_reading)
    await start_measure(client)
    try:
        while max_measurements is None or i < max_measurements:
            await asyncio.sleep(0.1)  # 
    except asyncio.exceptions.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    await client.stop_notify(TENG_READING_CUUID)
    await stop_measurement(client)
    _buffer.data = np.vstack((timestamps, np.zeros(len(timestamps)), readings)).T
    print("Measurement stopped" + " "*50)

def measure(client, interval, update_func=None, max_measurements=None):
    runner.run(_measure_async(client, interval=interval, update_func=update_func, max_measurements=max_measurements))
