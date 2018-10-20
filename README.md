# Neato-serial
Serial interface for Neato robot vacuum cleaners. Transforms your non-connected Neato into a connected one. Tested on XV Signature Pro and Raspberry Pi, should work on others. Uses [hub-ctrl.c](https://github.com/codazoda/hub-ctrl.c).

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values. See below for settings.

## Setup
Configuration values:

- serial:
  - *serial_device*: the device Neato is connected to. Multiple devices can be provided here, since after the USB connected has been temporarily switched off the device name might change.
    Example value: `/dev/ttyACM0,/dev/ttyACM1`
  - *timeout_seconds*: timeout in seconds to use for the serial connection. 
    Example value: `0.1`
  - *usb_switch_mode*: specifies if you connected Neato directly through a USB cable or through a relay.
  
    Options: `direct` or `relay`:
    - **direct**. Tested on Raspberry Pi 2 and 3. Does _not_ work on Raspberry Pi zero since usb port cannot be turned off - use **relay** instead. Connect your Pi and Neato directly using an USB cable:
![direct](raspberrypi-neato-direct.jpg?raw=true "Direct")
  
      This option does require elevated permissions (`sudo`) for the script since it needs to disable the usb port and (depending on config) reboot the Pi.
    - **relay**. Switches the USB connection using a relay. Tested to work on Raspberry Pi zero and others. This is the only method that works on Raspberry Pi zero. Be sure to also specify the GPIO the relay is connected to with `relay_gpio`. Connect a 5V relay to your Raspberry Pi. Cut your USB wire and re-connect all the cables except the red one. Wire the red cable through the relay (one side into `Common` and the other into `NO` if you have three connectors on your relay). I used a [Grove Relay from Seeed](http://wiki.seeedstudio.com/Grove-Relay/) but any relay should do.
    ![direct](raspberrypi-neato-relay.jpg?raw=true "Relay")
        
    Example value: `direct`
  - *relay_gpio*: specifies the GPIO the relay is connected to when using `usb_switch_mode: relay`.
  - *reboot_after_usb_switch*: specifies to reboot after usb has been switched off. Usefull if your Raspberry Pi does not reconnect after the USB has been disabled and enabled. Use with caution and only when running this script as a service.
    Example value: True
- mqtt:
  - *host*:	MQTT host
  - *username*:	MQTT username
  - *password*:	MQTT password
  - *port*: MQTT port.
    Example value: `1883`
  - *command_topic*: MQTT topic for receiving commands.
    Example value: `vacuum/command`
  - *state_topic*: MQTT topic for publishing state.
    Example value: `vacuum/state`
  - *publish_wait_seconds*: Delay in seconds before updating state again.
    Example value: `5`

## Usage
Two modes are available (start either using `python3 xx.py`).
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, for integration in MQTT scenario. Built for integration with [Home Assistant via MQTT Vacuum component](https://www.home-assistant.io/components/vacuum.mqtt/) but should be usable elsewhere as well. Run this script as a service using systemctl to get the integration working (see provided `neatoserialmqtt.service` file). Sample configuration for Home Assistant:
```yaml
vacuum:
  - platform: mqtt
    name: "Neato"
    supported_features:
      - turn_on
      - turn_off
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
    payload_turn_off: "Clean Stop"
    payload_locate: "PlaySound 19"
    fan_speed_topic: "vacuum/state"
    fan_speed_template: "{{value_json.fan_speed}}"
  ```

## Commands
See [the Neato programmers manual](XV-ProgrammersManual-3_1.pdf) for available commands.
It seems that some commands are not listed in the manual:

    - `Clean Stop` stops the vacuum.
    - `Clean Room` also seems to be available. Have not got it to work though.
    
