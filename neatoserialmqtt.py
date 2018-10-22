
"""MQTT interface for Neato Serial."""
from config import settings
import json
import time
import logging
from systemd.journal import JournalHandler
import paho.mqtt.client as mqtt
from neatoserial import NeatoSerial


def on_message(client, userdata, msg):
    """Message received."""
    inp = msg.payload.decode('ascii')
    print("Message received: "+inp)
    feedback = ns.write(inp)
    client.publish(settings['mqtt']['state_topic'], feedback)
    print("Feedback from device: "+feedback)


log = logging.getLogger('NeatoSerialMQTT')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)
log.info("Starting")
client = mqtt.Client()
client.on_message = on_message
client.username_pw_set(settings['mqtt']['username'],
                       settings['mqtt']['password'])
log.info("Connecting")
client.connect(settings['mqtt']['host'], settings['mqtt']['port'])
client.subscribe(settings['mqtt']['command_topic'], qos=1)
log.info("Setting up serial")
ns = NeatoSerial()

log.info("Ready")
client.loop_start()
while True:
    try:
        data = {}
        data["battery_level"] = ns.getBatteryLevel()
        data["docked"] = ns.getExtPwrPresent()
        data["cleaning"] = ns.getCleaning()
        data["charging"] = ns.getChargingActive()
        data["fan_speed"] = ns.getVacuumRPM()
        error = ns.getError()
        errorsplit = error.split(' - ')
        log.info("Error from Neato: "+str(errorsplit))
        if len(errorsplit) == 2:
            # handle error 220 - which means we need to toggle the usb
            # to trigger a clean
            if int(errorsplit[0]) == 220:
                ns.toggleusb()
            data["error"] = errorsplit[1]
        else:
            data["error"] = error
        json_data = json.dumps(data)
        client.publish(settings['mqtt']['state_topic'], json_data)
        time.sleep(settings['mqtt']['publish_wait_seconds'])
    except Exception as ex:
        log.info("Error getting status: "+ex)
