
"""MQTT interface for Neato Serial."""
from config import settings
import json
import time
import os
import sys
import paho.mqtt.client as mqtt
from neatoserial import NeatoSerial
import logging


def on_message(client, userdata, msg):
    """Message received."""
    inp = msg.payload.decode('ascii')
    log.info("Message received: "+inp)
    feedback = ns.write(inp)
    client.publish(settings['mqtt']['state_topic'], feedback)
    log.info("Feedback from device: "+feedback)

def on_disconnect(client, userdata, rc):
    client.loop_stop(force=False)
    if rc != 0:
        log.info("Unexpected disconnection.")
    else:
        log.info("Disconnected.")

logging.basicConfig(level = logging.INFO)
log = logging.getLogger(__name__)
log.debug("Starting")
client = mqtt.Client()
client.on_message = on_message
client.on_disconnect= on_disconnect
client.username_pw_set(settings['mqtt']['username'],
                       settings['mqtt']['password'])
log.debug("Connecting")
client.connect(settings['mqtt']['host'], settings['mqtt']['port'])
client.subscribe(settings['mqtt']['command_topic'], qos=1)
log.debug("Setting up serial")
ns = NeatoSerial()

log.debug("Ready")
client.loop_start()
while True:
    #try:
    if not ns.getIsConnected():
        ns.reconnect()
    data = {}
    data["battery_level"] = ns.getBatteryLevel()
    data["docked"] = ns.getExtPwrPresent()
    data["cleaning"] = ns.getCleaning()
    data["charging"] = ns.getChargingActive()
    data["fan_speed"] = ns.getVacuumRPM()
    error = ns.getError()
    log.debug("Error from Neato: "+str(error))
    if error:
        # handle error 220 - which means we need to toggle the usb
        # to trigger a clean
        if int(error[0]) == 220:
            ns.toggleusb()
            ns.reconnect()
        data["error"] = error[1]
    json_data = json.dumps(data)
    log.debug("Sending MQTT message: "+str(json_data))
    client.publish(settings['mqtt']['state_topic'], json_data)
    time.sleep(settings['mqtt']['publish_wait_seconds'])
    #except Exception as ex:
    #    log.error("Error getting status: "+str(ex))
