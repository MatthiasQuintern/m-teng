import pyvisa


def init_keithley(beep_success=True):
    rm = pyvisa.ResourceManager('@py')
    resources = rm.list_resources()
    if len(resources) < 1:
        raise Exception("No resources found.")
    elif len(resources) == 1:
        print(f"Opening Resource {resources[0]}")
        keithley = rm.open_resource(resources[0])
        if beep_success: keithley.write("beeper.beep(0.5, 1000)")
        return keithley
    elif len(resources) > 1:
        print(f"Resources: {resources}")
        instr = int(input("Select an instrument (0-based index)"))
        keithley = rm.open_resource(resources[instr])
        if beep_success: keithley.write("beeper.beep(0.5, 1000)")
        return keithley

