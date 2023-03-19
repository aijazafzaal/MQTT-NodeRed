from hcsr04 import HCSR04
import time      
from machine import Pin, PWM  
from time import sleep
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import json
import gc
gc.collect()

  
# ESP32
sensor = HCSR04(trigger_pin=21, echo_pin=22, echo_timeout_us=10000)

frequency = 15000       
pin1 = Pin(4, Pin.OUT)    
pin2 = Pin(18, Pin.OUT)     

ssid = 'Go To Hell'
password = '52646254'
mqtt_server = '192.168.2.110'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'esp/control'
topic_pub = b'esp/ulterasonic/value'




last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'esp/control' and msg == b'forward':
      pin1.on()
      pin2.off()
      print('ESP received hello message')
  if topic == b'esp/control' and msg == b'backward':
      pin1.off()
      pin2.on()
      #dc_motor.backwards(100)
      print('ESP received hello message')
  if topic == b'esp/control' and msg == b'stop':
      pin1.off()
      pin2.off()
      #de_motor.stop()
    

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()
  


while True:
    client.check_msg()
    try:
        if (time.time() - last_message) > message_interval:
            distance = sensor.distance_cm()
            dist = str(int(distance))
            print('Distance:', dist, 'cm')
            client.publish(topic_pub, dist)
            last_message = time.time()
            
    except OSError as e:
        restart_and_reconnect()

    
