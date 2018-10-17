"""MQTT interface for Neato Serial."""
from config import settings
import json
import time
import paho.mqtt.client as mqtt
from neatoserial import NeatoSerial


def on_message(client, userdata, msg):
    """Message received."""
    inp = msg.payload.decode('ascii')
    print("Message received: "+inp)
    feedback = ns.write(inp)
    client.publish(settings['mqtt']['state_topic'], feedback)
    print("Feedback from device: "+feedback)


print("Starting")
client = mqtt.Client()
client.on_message = on_message
client.username_pw_set(settings['mqtt']['username'],
                       settings['mqtt']['password'])
print("Connecting")
client.connect(settings['mqtt']['host'], settings['mqtt']['port'])
client.subscribe(settings['mqtt']['command_topic'], qos=1)
print("Setting up serial")
ns = NeatoSerial()

print("Ready")
client.loop_start()
while True:
    try:
        data = {}
        data["battery_level"] = ns.getBatteryLevel()
        data["docked"] = ns.getExtPwrPresent()
        data["cleaning"] = ns.getCleaning()
        data["charging"] = ns.getChargingActive()
        data["fan_speed"] = ns.getVacuumRPM()
        json_data = json.dumps(data)
        client.publish(settings['mqtt']['state_topic'], json_data)
        time.sleep(settings['mqtt']['publish_wait_seconds'])
    except:
        print("Error getting status.")
