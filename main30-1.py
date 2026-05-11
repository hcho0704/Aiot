import paho.mqtt.client as mqtt
import time
from gpiozero import LED
import threading

greenLed = LED(16)
blueLed = LED(20)
redLed = LED(21)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    message = msg.payload.decode()
    print(message)
    if message == "green_on":
        greenLed.on()
    elif message == "green_off":
        greenLed.off()
    elif message == "blue_on":
        blueLed.on()
    elif message == "blue_off":
        blueLed.off()
    elif message == "red_on":
        redLed.on()
    elif message == "red_off":
        redLed.off()

client = mqtt.Client()
client.on_message = on_message

broker_address="192.168.137.230"
client.connect(broker_address)
client.subscribe("led",1)

count = 0
def send_thread():
    global count
    while 1:
        count = count + 1
        client.publish("hello", str(count))
        time.sleep(1.0)

task = threading.Thread(target = send_thread)
task.start()

client.loop_forever()
