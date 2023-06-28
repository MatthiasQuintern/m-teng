# m-TENG
Helper scripts and shell for measuring **T**ribo**e**lectric **N**ano**g**enerator-based sensor output with a Keithley 2600B SMU or an Arduino

## Features

### Interactive (shell) mode
- Live view
- Press button to stop
- Save and load settings (default interval, data directory...)
- Easily run arbitrary command on device


### Useful functions for scripts
- Measure voltage and/or current
- Transfer buffer from measurement device to host
- Save/load as csv
- Run lua script on Keithley SMU
- Auto-filenames


## Available backends
### keithley
    Use a Keithley 2600B Source-Measure-Unit via *pyvisa*. This backend allows measuring both voltage and current simultaneously. *Tested with 2611B and 2614B*

### arduino
    Use a Bluetooth capable Arduino with [https://git.quintern.xyz/MatthiasQuintern/teng-arduino](this software on the arduino).
    This backend only allows measuring voltage using an Arduinos analog input pin (0 - 3.3 V, 12 bit resolution).

### testing
    Use the shell without measuring TENG output. When starting a measurement, sample data will be generated.


## Shell mode
It is recommended to run the shell with ipython:
```shell
ipython -i k_teng_interactive.py -- -*X*
```
Substitute *X* for `-k` for keithley backend, `-a` for arduino backend or `-t` for testing backend.

In the shell, run `help()` to get a list of available commands


## Installation
### Keithley
On linux:
Install the udev rule in `/etc/udev/rules.d/` and run `sudo udevadm control --reload` to force the usbtmc driver to be used with the Keithley SMU.
The `ATTRS{product_id} ` needs to match the id shown by `lsusb`.
