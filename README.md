# Neato-serial
Serial interface for Neato robot vacuum cleaners. Transforms your non-connected Neato into a connected one. Tested on XV Signature Pro and Raspberry Pi, should work on others. Uses [hub-ctrl.c](https://github.com/codazoda/hub-ctrl.c). [Demo video](https://1drv.ms/v/s!AgiTl-Kme52yxtd8ciTFaWSZh6yjjw)

## Hardware required
- Raspberry Pi (2, 3 and Zero tested and confirmed working) or any other device that runs Python and has some sort of GPIO and USB connectivity.
- A mini usb cable to connect your Raspberry Pi to Neato
- A micro usb cable to power your Raspberry Pi
- A 5V step-down voltage regulator. I used one from [Pololu](https://www.pololu.com/product/2858) but any should do. Make sure it can handle at least 16V as that is what Neato will be providing to power your Raspberry Pi from.
- A 5V relay (optional). I used a [Grove Relay from Seeed](http://wiki.seeedstudio.com/Grove-Relay/) but any 5v relay should do. The package also allows for direct USB connection, without a relay.

## Setup
- Connect to your step-down voltage regulator to Neato's 16V connection. See image below to find the right connector on the Neato motherboard:
![direct](neato-16v.jpg?raw=true "16V")
- Connect the output of the step-down voltage regulator (that should be 5V) to your Raspberry Pi's USB connector for power. Do not use the GPIO to power the Raspberry Pi directly.
- Connect a mini usb cable from the Raspberry Pi to Neato. 
- If using a relay:
  - connect it to the 5V, GND and GPIO 2 of your Raspberry Pi. If you use another GPIO make sure to reflect that in the configuration file (see below)
  - cut open the mini usb cable that you used to connect the Raspberry Pi to Neato, reconnect all wires except the red one (power). Run the red wire through the relay. See image below.

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- install [python-systemd](https://github.com/systemd/python-systemd/) by running `sudo apt-get install python3-systemd`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values. See below for settings.

## Configuration
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
    - `Clean Spot` tells the vacuum to do a spot clean
    
