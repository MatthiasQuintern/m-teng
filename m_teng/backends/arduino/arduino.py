import bleak as b
import asyncio
import numpy as np

TARGET_NAME = "ArduinoTENG"

# GATT service and characteristics UUIDs
TENG_SUUID          = "00010000-9a74-4b30-9361-4a16ec09930f"
TENG_STATUS_CUUID   = "00010001-9a74-4b30-9361-4a16ec09930f"
TENG_COMMAND_CUUID  = "00010002-9a74-4b30-9361-4a16ec09930f"
TENG_READING_CUUID  = "00010003-9a74-4b30-9361-4a16ec09930f"
TENG_COUNT_CUUID    = "00010004-9a74-4b30-9361-4a16ec09930f"
TENG_INTERVAL_CUUID = "00010005-9a74-4b30-9361-4a16ec09930f"

TENG_COMMANDS = {
    "STOP":             int(0).to_bytes(1, signed=False),
    "MEASURE_COUNT":    int(1).to_bytes(1, signed=False),
    "MEASURE":          int(2).to_bytes(1, signed=False),
}
TENG_STATUS = ["ERROR", "BUSY", "WAIT_CONNECT", "CONNECTED", "MEASURING"]

# TODO save measurements on device buffer, transfer later


# wrapper for global variable
class Buffer:
    def __init__(self):
        self.data = None
_buffer = Buffer()

# class Runner:
#     def __init__(self):
runner = asyncio.Runner()

def teng_status_callback(characteristic, data):
    value = int.from_bytes(data, byteorder="big", signed=False)
    if 0 <= value and value < len(TENG_STATUS):
        print(f"Status change: {TENG_STATUS[value]}")
    else:
        print(f"Status change (invalid): status={value}")


def disconnect_callback(client):
    raise Exception(f"The Bluetooth device {client.name} was disconnected")


async def init_arduino_async(n_tries: int=5) -> b.BleakClient:
    n_try = 0
    if n_tries <= 0: n_tries = "inf"
    try:
        target_device = None
        while target_device is None and (n_tries == "inf" or n_try < n_tries):
            print(f"Searching for Bluetooth device '{TARGET_NAME}' ({n_try+1}/{n_tries})", end="\r")
            devices = await b.BleakScanner.discover(return_adv=True, timeout=1.5)
            # print(devices)
            for adr, (device, adv_data) in devices.items():
                if device.name == TARGET_NAME:
                    # print(adv_data)
                    target_device = device
                    break
            n_try += 1
        if target_device is None:
            raise Exception(f"Could not find Bluetooth device 'ArduinoTENG'")
        # print(f"Found target device: {target_device.name}: {target_device.metadata}, {target_device.details}")
        # print(target_device.name, target_device.details)
        client = b.BleakClient(target_device, disconnect_callback=disconnect_callback)
        await client.connect()
        print(f"Connected to Bluetooth device '{TARGET_NAME}' at [{client.address}]")
        return client
    except asyncio.exceptions.CancelledError:
        raise Exception(f"Cancelled")


def init(beep_success=True, n_tries: int=5) -> b.BleakClient:
    """
    Connect to the arduino
    @returns: BleakClient
    """
    client = runner.run(init_arduino_async(n_tries=n_tries))
    if beep_success: beep(client)
    return client


def exit(client):
    try:
        runner.run(stop_measurement(client))
        runner.run(client.disconnect())
    except Exception:
        pass


async def set_interval(client, interval: float):
    """
    Set the measurement interval
    @param interval: interval in seconds
    """
    interval = int(interval * 1000)  # convert to ms for arduinos delay)
    await client.write_gatt_char(TENG_INTERVAL_CUUID, interval.to_bytes(2, byteorder="little", signed=False))

async def set_count(client, count: int):
    """
    Set the measurement count
    @param count: number of measurements to take
    """
    await client.write_gatt_char(TENG_COUNT_CUUID, count.to_bytes(2, byteorder="little", signed=False))

async def stop_measurement(client):
    await client.write_gatt_char(TENG_COMMAND_CUUID, TENG_COMMANDS["STOP"])

async def start_measure_count(client):
    await client.write_gatt_char(TENG_COMMAND_CUUID, TENG_COMMANDS["MEASURE_COUNT"])

async def start_measure(client):
    await client.write_gatt_char(TENG_COMMAND_CUUID, TENG_COMMANDS["MEASURE"])


# async def main():
#             for service in client.services:
#                 print(f"Service: {service.uuid}: {service.description}")
#                 for c in service.characteristics:
#                     print(f"\t{c.uuid}: {c.properties}, {c.descriptors}")
#             teng_status     = client.services.get_characteristic(TENG_STATUS_CUUID)
#             teng_command    = client.services.get_characteristic(TENG_COMMAND_CUUID)
#             teng_reading    = client.services.get_characteristic(TENG_READING_CUUID)
#             client.start_notify(teng_status, teng_status_callback)

#             await client.write_gatt_char(teng_command, TENG_COMMANDS["NOOP"])
#             await asyncio.sleep(5)
#             await client.write_gatt_char(teng_command, TENG_COMMANDS["MEASURE_BASELINE"])

#             while client.is_connected:
#                 data = await client.read_gatt_char(teng_reading)


#                 value = int.from_bytes(data, byteorder="little", signed=False)
#                 print(f"Reading: {value}")
#                 await asyncio.sleep(0.5)
#     except KeyboardInterrupt:
#         pass
#     except asyncio.exceptions.CancelledError:
#         pass
#     print("Disconnected")


def collect_buffer(instr, buffer_nr=1):
    """
    @param buffer_nr: 1 -> current, 2 -> voltage
    """
    assert(buffer_nr in (1, 2))
    return np.vstack((_buffer.data[:,0], _buffer.data[:,buffer_nr])).T


def beep(client):
    # TODO connect beeper to arduino?
    print("beep")
