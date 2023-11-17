from . import psu, utils

if __name__ == '__main__':

    # Start up a power supply instance which can be communicated through COM Port 79
    supply = psu.Supply(79)

    # Power ON the device
    supply.enable()

    # Read all the power supply readings which includes the Voltage, Current and Power Supply Mode
    supply.reading()