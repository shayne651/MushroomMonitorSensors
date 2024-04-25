# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from machine import Pin, SoftI2C
import sys
import time

''' Minimal example for operating the HDC1080 sensor.

The HDC1080 sensor module is measuring relative air humidity 
and temperature. Here, it is wired to an ESP32 developer 
board. 

Connect the ESP32 board via USB cable with your computer. 

You may use picocom <portname> -b115200 to see the measurement 
results. The portname is individual. On a Linux system, 
it is most likely something like /dev/ttyUSB0. 
'''

# Standard address of the HDC sensor:
HDC_ADDR = 64

# Registers storing temperature and humidity (see data sheet):
TMP_REG = 0x00
HUM_REG = 0x01

# Wirering of the SoftI2C bus:
# scl (clock)
# sda (data)
SCL = 22 # pin number
SDA = 21 # pin number

# Measurment frequency in seconds:
DELAY = 15


def init_i2c():
    """Init the SoftI2C bus."""
    i2c = SoftI2C(scl=Pin(SCL, Pin.OUT, Pin.PULL_UP),
              sda=Pin(SDA, Pin.OUT, Pin.PULL_UP),
              freq=100000)
    return(i2c)

def check_sensors(i2c):
    """Check if sensors are present at the expected addresses."""
    if HDC_ADDR not in i2c.scan():
        print('HDC 1080 not found at 7 bit address 64.')
        print('Found devices at: ' + str(i2c.scan()) )
        sys.exit()
        
def get_temperature(i2c):
    ''' Read temperature sensor.

    Returns: Temperature in degrees Celsius.
    '''
    # Point to temperature register:
    i2c.writeto(HDC_ADDR, bytearray([TMP_REG]))
    # Hold on (conversion time, data sheet):
    time.sleep(0.0635)
    # Read two bytes:
    tmp_bytes = i2c.readfrom(HDC_ADDR, 2)
    # Convert to temperature (formula from data sheet):
    tmp_deg_c = (int.from_bytes(tmp_bytes, 'big') / 2**16) * 165 - 40
    return(tmp_deg_c)

def get_humidity(i2c):
    ''' Read humidity sensor.

    Returns: Percent relative Humidity.
    '''
    # Point to humidity register:
    i2c.writeto(HDC_ADDR, bytearray([HUM_REG]))
    # Hold on (conversion time, data sheet):
    time.sleep(0.065)
    # Read two bytes:
    hum_bytes = i2c.readfrom(HDC_ADDR, 2)
    # Convert to percent relative humidity (formula from data sheet):
    hum_p_rel = (int.from_bytes(hum_bytes, 'big') / 2**16) * 100
    return(hum_p_rel)

def log_data(i2c):
    """Print data to stdout."""
    while True:
        # get the measurement data
        tmp_deg_c = get_temperature(i2c)
        hum_p_rel = get_humidity(i2c)
        # print data
        print('{:.2f} deg C'.format(tmp_deg_c))
        print('{:.2f} percent rel. humidity'.format(hum_p_rel))
        time.sleep(DELAY)
