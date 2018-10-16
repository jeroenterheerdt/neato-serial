# neato-serial
Serial interface for Neato robot vacuum cleaners. Testing on XV Signature Pro and Raspberry Pi, should work on others.

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values. See below for setting for `usb_switch_mode`.

## Setup
To connect your Raspberry Pi to Neato two options are provided:
- direct. Tested on Raspberry Pi 2 and 3. Does _not_ work on Raspberry Pi zero - use relay instead. Connect your Pi and Neato directly using an USB cable:
!(raspberrypi-neato-direct.jpg)
- relay. Tested on Raspberry Pi 2, 3 and Zero. 


## Usage
Two modes are available (start either using `python3 xx.py`)
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, for integration in MQTT scenario. Built for integration with [Home Assistant via MQTT Vacuum component](https://www.home-assistant.io/components/vacuum.mqtt/) but should be usable elsewhere as well.
