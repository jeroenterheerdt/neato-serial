"""Serial interface for Neato."""
from config import settings
import serial
import os
import time
import RPi.GPIO as GPIO
import logging


class NeatoSerial:
    """Serial interface to Neato."""

    def __init__(self):
        """Initialize serial connection to Neato."""
        logging.basicConfig(level="INFO")
        self.log = logging.getLogger(__name__)
        if settings['serial']['usb_switch_mode'] == 'relay':
            # use relay to temporarily disconnect neato to trigger clean
            self.pin = int(settings['serial']['relay_gpio'])
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.output(self.pin, GPIO.HIGH)
        self.isConnected = self.connect()

    def connect(self):
        """Connect to serial port."""
        devices = settings['serial']['serial_device'].split(',')
        for dev in devices:
            try:
                self.ser = serial.Serial(dev, 115200,
                                         serial.EIGHTBITS, serial.PARITY_NONE,
                                         serial.STOPBITS_ONE,
                                         settings['serial']['timeout_seconds'])
                self.open()
                self.log.debug("Connected to Neato at "+dev)
                return True
            except:
                self.log.error("Could not connect to device "+dev+". "
                               + "Trying next device.")
        return False

    def getIsConnected(self):
        """Return if connected."""
        return self.isConnected

    def open(self):
        """Open serial port and flush the input."""
        if self.ser is None:
            return
        else:
            self.ser.isOpen()
            self.ser.flushInput()

    def close(self):
        """Close serial port."""
        self.ser.close()
        self.isConnected = False

    def read_all(self, port, chunk_size=200):
        """Read all characters on the serial port and return them."""
        if not port.timeout:
            raise TypeError('Port needs to have a timeout set!')
        read_buffer = b''
        while True:
            # Read in chunks. Each chunk will wait as long as specified by
            # timeout. Increase chunk_size to fail quicker
            byte_chunk = port.read(size=chunk_size)
            read_buffer += byte_chunk
            if not len(byte_chunk) == chunk_size:
                break
        return read_buffer

    def toggleusb(self):
        """Toggle USB connection to Neato."""
        if settings['serial']['usb_switch_mode'] == 'direct':
            self.log.debug("Direct connection specified.")
            # disable and re-enable usb ports to trigger clean
            os.system('sudo ./hub-ctrl -h 0 -P 2 -p 0 ; sleep 1; '
                      + 'sudo ./hub-ctrl -h 0 -P 2 -p 1 ')
        elif settings['serial']['usb_switch_mode'] == 'relay':
            self.log.debug("Relay connection specified")
            # use relay to temporarily disconnect neato to trigger clean
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(1)
            GPIO.output(self.pin, GPIO.HIGH)
        if settings['serial']['reboot_after_usb_switch']:
            os.system('sudo reboot')

    def reconnect(self):
        """Close and reconnect connection to Neato."""
        self.log.debug("Reconnecting to Neato")
        time.sleep(5)
        self.close()
        self.isConnected = self.connect()
        self.open()

    def handleCleanMessage(self, msg):
        """Handle sending and extra activities for Clean messages."""
        inp = msg+"\n"
        self.ser.write(inp.encode('utf-8'))
        # toggle usb
        self.log.debug("Message started with 'Clean' so toggling USB")
        self.toggleusb()
        # the device might have changed with the usb toggle,
        # so let's close and reconnect
        self.reconnect()
        # we might have to send the message twice to start the actual cleaning
        if self.getIsConnected() and not self.getCleaning():
            self.ser.write(inp.encode('utf-8'))
            self.log.debug("Resent 'Clean' message so toggling USB")
            self.toggleusb()
            self.reconnect()

    def write(self, msg):
        """Write message to serial and return output."""
        self.log.debug("Message received for writing: "+msg)
        if self.isConnected:
            # wake up neato by sending something random
            try:
                self.ser.write("wake-up\n".encode('utf-8'))
                time.sleep(1)
                out = ''
                while self.ser.inWaiting() > 0:
                    out += self.read_all(self.ser).decode('utf-8')
                # now send the real message
                if msg.startswith("Clean"):
                    self.handleCleanMessage(msg)
                else:
                    inp = msg+"\n"
                    self.ser.write(inp.encode('utf-8'))
                out = ''
                # let's wait one second before reading output
                time.sleep(1)
                while self.ser.inWaiting() > 0:
                    out += self.read_all(self.ser).decode('utf-8')
                    if out != '':
                        return out
            except OSError as ex:
                self.log.error("Exception in 'write' method: "+str(ex))
                self.reconnect()
        else:
            self.isConnected = self.connect()

    def getError(self):
        """Return error message if available."""
        output = self.write("GetErr")
        if output is not None:
            outputsplit = output.split('\r\n')
            if len(outputsplit) == 3:
                err = outputsplit[1]
                if ' - ' in err:
                    errsplit = err.split(' - ')
                    # if err is 220 (unplug usb before cleaning) handle it
                    if int(errsplit[0]) == 220:
                        self.toggleusb()
                        self.reconnect()
                    return errsplit[0], errsplit[1]
            else:
                return None
        else:
            return None

    def getBatteryLevel(self):
        """Return battery level."""
        charger = self.getCharger()
        if charger:
            return int(charger.get("FuelPercent", 0))
        else:
            return 0

    def getChargingActive(self):
        """Return true if device is currently charging."""
        charger = self.getCharger()
        if charger:
            return bool(int(charger.get("ChargingActive", False)))
        else:
            return False

    def getExtPwrPresent(self):
        """Return true if device is currently docked."""
        charger = self.getCharger()
        if charger:
            return bool(int(charger.get("ExtPwrPresent", False)))
        else:
            return False

    def getAccel(self):
        """Get accelerometer info."""
        return self.parseOutput(self.write("GetAccel"))

    def getAnalogSensors(self):
        """Get analog sensor info."""
        return self.parseOutput(self.write("GetAnalogSensors"))

    def getButtons(self):
        """Get button info."""
        return self.parseOutput(self.write("GetButtons"))

    def getCalInfo(self):
        """Get calibration info."""
        return self.parseOutput(self.write("GetCalInfo"))

    def getCharger(self):
        """Get charger info."""
        return self.parseOutput(self.write("GetCharger"))

    def getDigitalSensors(self):
        """Get digital sensor info."""
        return self.parseOutput(self.write("GetDigitalSensors"))

    def getLDSScan(self):
        """Get lidar scan."""
        return self.parseOutput(self.write("GetLDSScan"))

    def getMotors(self):
        """Get motor info."""
        return self.parseOutput(self.write("GetMotors"))

    def getVersion(self):
        """Get version info."""
        return self.parseOutput(self.write("GetVersion"))

    def getVacuumRPM(self):
        """Get vacuum RPM."""
        motors = self.getMotors()
        if motors:
            return int(motors.get("Vacuum_RPM", 0))
        else:
            return 0

    def getCleaning(self):
        """Return true is device is currently cleaning."""
        return self.getVacuumRPM() > 0

    def parseOutput(self, output):
        """Parse the raw output of the serial port into a dictionary."""
        if output is None:
            return None
        else:
            lines = output.splitlines()
            dict = {}
            for l in lines:
                lsplit = l.split(',')
                if len(lsplit) > 1:
                    dict[lsplit[0]] = lsplit[1]
            return dict


if __name__ == '__main__':
    ns = NeatoSerial()
    print("Enter commands. Enter 'exit' to quit")
    while 1:
        inp = input("? ")
        if inp == 'exit':
            ns.close()
            exit()
        else:
            try:
                print(">> "+ns.write(inp))
            except:
                print("No result returned.")
