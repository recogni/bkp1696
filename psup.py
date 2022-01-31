# Tested on python3
# Requirements
# pyserial
# pyusb
################################################################################
# -- Imports
################################################################################
from __future__ import division
import argparse
import serial
import sys
import glob
import time
import decimal
import datetime

################################################################################
# -- Defines/Constants
# lsusb -> ID 10c4:ea60 Silicon Labs CP210x UART Bridge
# BK_PRECISION_9104_PRODUCT_ID = 0xea60
# BK_PRECISION_9104_VENDOR_ID = 0x10c4
################################################################################

################################################################################
# -- Classes
################################################################################
def _str2num(num, factor=10):
    """Takes a number in the supply's format, which always has one
    decimal place, and returns a decimal number reflecting it.
    """
    return decimal.Decimal(num) / factor
def _num2str(s, length=3, factor=10):
    """Turns a number, which may be a decimal, integer, or float,
    and turns it into a supply-formatted string.
    """
    dec = decimal.Decimal(s)
    return ('%0' + str(length) + 'i') % int(dec * factor)
def _numfields(s, fields, factor=10):
    """Generates numbers of the given lengths in the string.
    """
    pos = 0
    for field in fields:
        yield _str2num(s[pos:pos+field], factor)
        pos += field

class Error(Exception):
    """Base class for exceptions in this module."""
    pass
class BaseSetup:
    """ Setup args """
    def __init__ (self):
        self.args = None
        self.dict_args = None
        self.debug = 0

    def arg_setup(self):
        """ Argument parser """
        dict_args = None
        self.args = None
        parser = argparse.ArgumentParser(description='BK Precision power control ',
        usage = ('psup --port /dev/power_serial --on'))
        #serial_parser = parser.add_mutually_exclusive_group(required=True)
        parser.add_argument('--port', type=str, help='serial port')
        parser.add_argument('--on', action='store_true', help='switch output on')
        parser.add_argument('--off', action='store_true', help='switch output off')
        parser.add_argument('--info', action='store_true', help='get PSU info')
        self.args = parser.parse_args()
        self.dict_args = vars(self.args)

class Supply(BaseSetup):
    def __init__(self, ident=None):
        super().__init__()

    def serial_port_init (self):
       # Intialize serial port based on programming manual
        self.ser = serial.Serial(str(self.args.port), 9600, 8, 'N', 1)

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
                     return resp

    # Lock the keypad.
    def start(self):
        self.command('SESS')

    # Unlock the keypad.
    def close(self):
        self.command('ENDS')

    def reading(self):
        resp = self.command('GETD')
        volts, amps = _numfields(resp, (4, 4), 1)
        return (volts/100), (amps/100)

    def enable(self):
        """Enable output."""
        self.command('SOUT1')
    def disable(self):
        """Disable output."""
        self.command('SOUT0')

    # Context manager "with" for "bk_supply"
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return self
    # Setting voltage and other SCPI commands are untested.
    def voltage(self, volts):
        print(_num2str(volts))
        #self.command('VOLT', _num2str(volts))
    def maxima(self):
        resp = self.command('GMAX')
        return tuple(_numfields(resp, (3, 3)))
    def settings(self):
        resp = self.command('GETS')
        return tuple(_numfields(resp, (3, 3)))

###############################################################################
# -- Main function
###############################################################################
# -- Main function
def main():
    """ Main function """
    bk_supply=Supply()
    # Get inputs
    try:
        bk_supply.arg_setup()
        bk_supply.serial_port_init()
    except:
        bk_supply.parser.print_help()
        sys.ext(0)
    # Switch ON supply.
    with bk_supply as sup:
        if sup.args.on is True:
            sup.enable()
            time.sleep(0.5)
        # Switch OFF supply
        elif sup.args.off:
            sup.disable()
        # Get status of supply
        else:
            volts,amps= sup.reading()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(volts), ' Volts ')
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(amps), ' Amps ')
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(amps*volts), ' Watts ')
    time.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except Error as e:
        print (e)
        exit(1)