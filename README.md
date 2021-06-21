# Neato-serial
Serial interface for Neato robot vacuum cleaners. Transforms your non-connected Neato into a connected one. Tested on XV Signature Pro and Raspberry Pi, should work on others.  [Demo video](https://1drv.ms/v/s!AgiTl-Kme52yxtd8ciTFaWSZh6yjjw). Uses [hub-ctrl.c](https://github.com/codazoda/hub-ctrl.c).

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
 
 ## Setup - 2021 update (Internal housing) - RobertD502
 **Hardware Used:**
 1. Raspberry Pi ZeroW (Will sit on top of Neato motherboard in the upper left hand corner)
 2. [5V step-down voltage regulator](https://www.amazon.com/gp/product/B08JZ5FVLC) - if using this exact voltage-regulator, I recommend removing the pot (little wheel in the upper right-hand corner) before soldering the 5V pad on the back as there have been reports of voltage variation when it is kept. The pot can be removed by applying heat to the side of it at the top with a soldering iron.
 3. [5V Relay](https://www.amazon.com/Flymmy-Raspberry-Arduino-Channel-Opto-Isolated/dp/B0824R8NG2)
 4. [Kapton Tape](https://www.amazon.com/gp/product/B072Z92QZ2) to prevent any shorts
 5. [3-Wire JST Connector](https://www.amazon.com/BTF-LIGHTING-Connectors-WS2812B-WS2811-WS2812/dp/B01DC0KIT2) (**optional**) - I wired a JST connector to the Neato MiniUSB side and another to the Raspberry Pi MicroUSB port to allow me to disconnect the Pi if needed in the future. This is completely optional and a personal preference.
 6. [Ferule + Ferule Crimping tool](https://www.amazon.com/Ferrule-Crimping-Tools-Wire-Pliers/dp/B07WRQN45C) (**optional**) - It is good practice to add ferules to wires which will be held in place by screw terminals instead of leaving exposed bare wires.
 
 **Wiring**
 * Remove the two wires from the Neato's 16V connector and solder an additional wire to each of the pins. Place the wires back into the connector (See image below).
 ![direct](Neato-16V-Soldered.jpg?raw=true "16V-S")
 * Voltage-Regulator Wiring:
   * If using the voltage-regulator mentioned above, be sure to remove the pot and solder the 5V pads on the back of voltage-regulator. 
   * Solder the live wire (red wire) from Neato's 16V connector (previous step) to the port labeled `IN+` on the voltage-regulator.
   * Solder the ground wire (black wire) from Neato's 16V connector to the port labeled `GND` on the voltage-regulator.
 * Power to the Raspberry Pi ZeroW:
   * Solder an additional wire to the port labeled `GND` on the voltage-regulator and the other end to the test point labeled `PP6` on the underside of the Raspberry Pi ZeroW (see image below).
   * Solder a wire to the port labeled `VO+` on the voltage-regulator and the other end to the test point labeled `PP1` on the underside of the Raspberry Pi ZeroW (see image below).
   * The port labeled `EN` on the voltage-regulator will not be used
   * ![direct](pi-zerow-test-points.jpeg?raw=true "ZeroW-Test-Points")
 * Wiring Raspberry Pi ZeroW to Relay
   * You can either use dupont connectors to connect the Pi to the relay or solder wires to the pins on the underside of the Pi.
   * Connect your relay to the 5V, GND and GPIO 2 of your Raspberry Pi. If you use another GPIO make sure to reflect that in the configuration file (see `Configuration` Section). If using a relay with screw-terminals, I recommend using ferules on the ends of the wires going into the relay screw terminals. Also, be sure to use enough wire length to allow the wires to reach from the upper-left side of the motherboard where the Pi will sit to a hole near the left wheel where the relay will sit (See image below).
   * Solder another wire (preferably red) to the test point labeled `PP1` on the underside of the Raspberry Pi ZeroW and place the other end into the `COM` port of the relay.
   * We will come back to the relay in the next steps.
   * ![direct](neato-disassembled.jpeg?raw=true "Neato-Disassembled")
 * Wiring Pi ZeroW MicroUSB port to Neato's MiniUSB port:
   * **Warning**: When soldering to the pads on Neato's motherboard, DO NOT use high heat as these pads are weak and will pull off of the motherboard if not handled with care. Also, add some hot glue to the top of the wires/connections (once all 3 soldered connections are made) to help alleviate wire strain and prevent the pads from getting pulled up.
   * If you are using JST connectors that I mentioned in the hardware section, choose either a male or female connector for the Raspberry Pi side and the opposite for Neato side ( Female connector on Pi & Male connector on Neato side **or** Male connector on Pi & Female connector on Neato side).
   * **If using JST connectors:**
     - Solder the `green wire (D+)` of your JST connector to the small round pad above the component labeled `D13` (see image below)
     - Solder the `white wire (D-)` of your JST connector to the small round pad above the component labeled `D13` and to the left of the previously soldered green wire (see image below)
     - Solder the `red wire (VCC)` of your JST connector to the right-side of the resistor labeled `R90` (see image below)
     - Be sure to add hot glue to the connections at the Neato's motherboard to alleviate wire strain and prevent pads from lifting
     - With a new JST connector, solder the `green wire (D+)` to the test point labeled `PP22` on the underside of the Raspberry Pi ZeroW (image of test points located above)
     - Solder the `white wire (D-)` to the test point labeled `PP23` on the underside of the Raspberry Pi ZeroW (image of test points located above)
     - Solder the `red wire (VCC)` to a separate wire (be sure to add heat shrink tubing over the connection point of the two wires)- the other end of this wire goes into the relay port labeled `NO`
   * **If not using JST connectors:**
     - Solder a wire (preferably green) to the small round pad above the component labeled `D13` (pad labeled as `D+` in image below). Solder the other side of the wire to the test point labeled `PP22` on the underside of the Raspberry Pi ZeroW (image of test points located above)
     - Solder a wire (preferably white) to the small round pad above the component labeled `D13` (pad labeled as `D-` in image below). Solder the other side of the wire to the test point labeled `PP23` on the underside of the Raspberry Pi ZeroW (image of test points located above)
     - Solder a wire (preferably red) to the right-side of the resistor labeled `R90` (labeled as `VCC` in image below). Insert the other end of this wire into the relay port labeled `NO`
     - Be sure to add hot glue to the connections at the Neato's motherboard to alleviate wire strain and prevent pads from lifting
    * ![direct](neato-miniusb.jpg?raw=true "Neato-MiniUSB")
 * Wrapping up:
   * Cover the underside of the Raspberry Pi ZeroW and the entire voltage-regulator with Kapton tape to prevent any shorts from occuring.
   * ![direct](pi-kapton.jpg?raw=true "Pi-Kapton") ![direct](voltage-regulator-kapton.jpg?raw=true "VR-Kapton")     
 

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
  - *discovery_topic*: auto-discovery topic. Example value: `hass` 
    Uncomment this and add your Home Assistant auto-discovery topic if you intend to have Home Assistant add the vacuum automatically. **If you intend to manually (legacy method) set the vacuum up in Home Assistant leave this commented out - See sample configuration under `Usage` section if using legacy method.**
  - *command_topic*: MQTT topic for receiving commands.
    Example value: `vacuum/command`
  - *state_topic*: MQTT topic for publishing state.
    Example value: `vacuum/state`
  - *publish_wait_seconds*: Delay in seconds before updating state again.
    Example value: `5`

## Usage
Two modes are available (start either using `python3 xx.py`).
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, for integration in MQTT scenario. Built for integration with [Home Assistant via MQTT Vacuum component](https://www.home-assistant.io/components/vacuum.mqtt/) but should be usable elsewhere as well. Run this script as a service using systemctl to get the integration working (see provided `neatoserialmqtt.service` file). 
- Sample configuration for Home Assistant:
  * If you defined a `discovery-topic` in the configuration file, you do not need to do this.
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
    
