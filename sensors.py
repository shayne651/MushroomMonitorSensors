from machine import Pin
from umqtt.simple import MQTTClient
from hdc1080 import *

def turnOnHumidity():
    Pin(5, mode=Pin.OUT)
    
def turnOffHumidity():
    Pin(5, mode=Pin.IN)
    
def turnOnFea():
    Pin(6, mode=Pin.IN)
    
def turnOffFea():
    Pin(6, mode=Pin.OUT)
    
def checkSensors(i2c, minHumidity, maxHumidity):
    humidity = get_humidity(i2c)
    temp = get_temperature(i2c)
    if humidity < minHumidity:
        turnOnHumidity()
    else:
        turnOffHumidity()
        
def runFea(runtime):
    turnOnFea()
    sleep(runtime)
    turnOffSensor()
