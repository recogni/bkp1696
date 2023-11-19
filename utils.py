################################################################################
# -- Imports
################################################################################
from __future__ import division
import time
import sys
import decimal

################################################################################
# -- Supporting Functions
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

def pretty_sleep(sec):
    for remaining in range(sec, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} second(s) remaining.   ".format(remaining))
        sys.stdout.flush()
        time.sleep(0.3333)
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} second(s) remaining..  ".format(remaining))
        sys.stdout.flush()
        time.sleep(0.3333)
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} second(s) remaining... ".format(remaining))
        sys.stdout.flush()
        time.sleep(0.3333)
    sys.stdout.write("\rDone Waiting!            \n")