# neato-serial
Serial interface for Neato robot vacuum cleaners. Testing on XV Signature Pro and Raspberry Pi, should work on others.

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values. See below for setting for `usb_switch_mode`.

## Setup
To connect your Raspberry Pi to Neato two options are provided:
- **direct**. Tested on Raspberry Pi 2 and 3. Does _not_ work on Raspberry Pi zero - use relay instead. Connect your Pi and Neato directly using an USB cable:
![direct](raspberrypi-neato-direct.jpg?raw=true "Direct")
- **relay**. Tested on Raspberry Pi 2, 3 and Zero. 


## Usage
Two modes are available (start either using `python3 xx.py`)
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, for integration in MQTT scenario. Built for integration with [Home Assistant via MQTT Vacuum component](https://www.home-assistant.io/components/vacuum.mqtt/) but should be usable elsewhere as well. Run this script as a service using systemctl to get the integration working. Sample configuration for Home Assistant:
```yaml
vacuum:
  - platform: mqtt
    name: "Neato"
    supported_features:
      - turn_on
      - send_command
      - battery
      - status
      - locate
    command_topic: "vacuum/command"
    battery_level_topic: "vacuum/state"
    battery_level_template: "{{value_json.battery_level}}"
    charging_topic: "vacuum/state"
    charging_template: "{{value_json.charging}}"
    cleaning_topic: "vacuum/state"
    cleaning_template: "{{value_json.cleaning}}"
    docked_topic: "vacuum/state"
    docked_template: "{{value_json.docked}}"
    send_command_topic: "vacuum/command"
    payload_turn_on: "Clean"
    payload_locate: "PlaySound 19"
    fan_speed_topic: "vacuum/state"
    fan_speed_template: "{{value_json.fan_speed}}"
  ```

## Commands
See [the Neato programmers manual](XV-ProgrammersManual-3_1.pdf) for available commands.
