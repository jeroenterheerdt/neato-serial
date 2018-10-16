# neato-serial
Serial interface for Neato robot vacuum cleaners. Testing on XV Signature Pro, should work on others.

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values.


## Usage
Two modes are available (start either using `python3 xx.py`)
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, for integration in MQTT scenario. Built for integration with [Home Assistant via MQTT Vacuum component](https://www.home-assistant.io/components/vacuum.mqtt/) but should be usable elsewhere as well.
