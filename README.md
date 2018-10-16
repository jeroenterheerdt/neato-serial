# neato-serial
Serial interface for Neato robot vacuum cleaners. Testing on XV Signature Pro, should work on others.

## Installation
- install the requirements using provided `requirements.txt`: `pip install -r requirements.txt`
- create `config.yaml` by copying the `config.yaml.example` provided and setting the correct values.


## Usage
Two modes are available:
- interactive console mode: `neatoserial.py`
- mqtt mode: `neatoserialmqtt.py`, built for integration with (https://www.home-assistant.io/components/vacuum.mqtt/)[Home Assistant via MQTT Vacuum component].
