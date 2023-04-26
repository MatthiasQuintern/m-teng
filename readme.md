# K-TENG
Helper scripts and shell for measuring **T**ribo**e**lectric **N**ano**g**enerator-based sensor output with a Keithley 2611B SMU using pyvisa

## Features
### Useful functions for scripts
- Measure Voltage and/or Current
- Transfer buffer from device to host
- Save/load as csv
- Run lua script on device
- Auto-filenames
### Interactive (shell) mode
- Live view
- Press button to stop
- Save and load settings (default interval, data directory...)
- Easily run arbitrary command on device

## Shell mode
Start with:
```shell
ipython -i k_teng_interactive.py
```

Use `help()` to get a list of available commands
