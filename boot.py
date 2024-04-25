from hdc1080 import *
import network
from umqtt.simple import MQTTClient
from machine import Pin
from time import sleep
import json
import struct
from sensors import checkSensors, runFea

i2c = init_i2c()
check_sensors(i2c)

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('<SSID_ID>', '<SSID_PASS>')
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())

CLIENT_NAME = 'mushroom_monitor-test'
BROKER_ADDR = '<HOST>'
PORT = '<PORT>'
USERNAME = '<USER>'
PASSWORD = '<PASS>'
mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, PORT, USERNAME, PASSWORD)
mqttc.connect()

# Default values
minHumidity = 0
maxHumidity = 0
minTemp = 0
maxTemp = 0

def handleIncoming(topicb, msg):
    topic = topicb.decode()
    if topic == "mushroom_monitor-test.config":
        updateConfig(msg)
    elif topic == "mushroom_monitor-test.fea":
        run_fea(msg)

def updateConfig(msg):
    global minHumidity, maxHumidity, minTemp, maxTemp
    message = json.loads(msg.decode())
    minHumidity = message['minHumidity']
    maxHumidity = message['maxHumidity']
    minTemp = message['minTemp']
    maxTemp = message['maxTemp']
    print(message['maxTemp'])
    
def run_fea(msg):
    message = json.loads(msg.decode())
    runFea(message['runtime'])
        
# mqtt subscription
mqttc.set_callback(handleIncoming)
mqttc.subscribe('mushroom_monitor-test.config')
mqttc.subscribe('mushroom_monitor-test.fea')

while True:
    mqttc.check_msg()
    humidity = get_humidity(i2c)
    temp = get_temperature(i2c)
    checkSensors(i2c, minHumidity, maxHumidity)
    mqttc.publish("mushroom_monitor-test.humidity", str(humidity))
    mqttc.publish("mushroom_monitor-test.temp", str(temp))
    if minHumidity == 0 or maxHumidity == 0:
        mqttc.publish("mushroom_monitor-test.request-config", str(True))
    sleep(10)
