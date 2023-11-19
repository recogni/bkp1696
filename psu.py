################################################################################
# -- Imports
################################################################################
import serial
from enum import Enum
from . import utils

################################################################################
# -- Defines/Constants
# lsusb -> ID 10c4:ea60 Silicon Labs CP210x UART Bridge
# BK_PRECISION_9104_PRODUCT_ID = 0xea60
# BK_PRECISION_9104_VENDOR_ID = 0x10c4
################################################################################

################################################################################
# -- Classes
################################################################################

# Preset ENUM Class
class PRESET(Enum):
    A = 0
    B = 1
    C = 2

    def get_preset_value(preset):
        return preset.value

    def get_preset_value_from_name(name):
        return PRESET.__members__[name].value

# TODO: Add custom exceptions for BK 9104 Power Supply
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

# Main BK 910x Power Supply Class
class Supply():

    # Supply Class constructor
    def __init__(self, port):
        # Instantiate the serial communication
        self.ser = serial.Serial("COM"+str(port), 9600, 8, 'N', 1)

    # Message Control
    def command(self, code, param='', address='00'):
        # Put this communication in an isolated little transaction.
        self.ser.flushInput()
        self.ser.flushOutput()
        serialcmd = code + "\r"
        #print (serialcmd)  #Debug only
        self.ser.write(serialcmd.encode())
        self.ser.flush()
        resp = ""
        out = None
        while True:
            resp = ''
            while True:
                char = self.ser.read()
                if (char != b'\r'):
                    resp += str(char,'utf-8')
                if (resp.find('OK') != -1):
                     return resp[:len(resp)-2]

    # Lock the keypad.
    def start(self):
        self.command('SESS')

    # Unlock the keypad.
    def close(self):
        self.command('ENDS')

    # Read Voltage, Current and CV/CC mode
    def reading(self):
        resp = self.command('GETD')
        print(resp)
        volts, amps, mode = utils._numfields(resp, (4, 4, 1), 1)
        return (volts/100), (amps/100), (mode)

    # Power ON the power supply
    def enable(self):
        self.command('SOUT1')

    # Power OFF the power supply
    def disable(self):
        self.command('SOUT0')

    # Context manager "with" for "bk_supply"
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return self

    # TODO: Add code to check if the command sent is successful
    def set_preset_values(self, preset='A', volt=0, curr=0):
        cmd = 'SETD' + ' ' + str(PRESET.get_preset_value_from_name(preset)) + utils._num2str(volt, length=4, factor=100) + utils._num2str(curr, length=4, factor=100)
        print(cmd)
        self.command(cmd)

    def select_preset(self, name):
        cmd = 'SABC' + ' ' + str(PRESET.get_preset_value_from_name(name))
        print(cmd)
        self.command(cmd)

    def set_output_voltage(self, preset='A', volt=0):
        cmd = 'VOLT' + ' ' + str(PRESET.get_preset_value_from_name(preset)) + utils._num2str(volt, length=4, factor=100)
        print(cmd)
        self.command(cmd)

    def set_output_current(self, preset='A', curr=0):
        cmd = 'CURR' + ' ' + str(PRESET.get_preset_value_from_name(preset)) + utils._num2str(curr, length=4, factor=100)
        print(cmd)
        self.command(cmd)

    # Untested method
    def maxima(self):
        resp = self.command('GMAX')
        return tuple(utils._numfields(resp, (3, 3)))

    # Untested method
    def settings(self):
        resp = self.command('GETS')
        print(resp)
        return tuple(utils._numfields(resp, (3, 3)))