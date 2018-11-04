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
        self.log = logging.getLogger(__name__)
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
                print("Connected to Neato at "+dev)
                return True
            except:
                self.log.error("Could not connect to device "+dev+". "
                               + "Trying next device.")
                print("Could not connect to device "+dev+". "
                      + "Trying next device.")
        return False

    def getIsConnected(self):
        """Return if connected."""
        return self.isConnected

    def open(self):
        """Open serial port and flush the input."""
        print("Entering OPEN()")
        if self.ser is None:
            return
        else:
            self.ser.isOpen()
            self.ser.flushInput()
        print("Leaving OPEN()")

    def close(self):
        """Close serial port."""
        print("Entering CLOSE()")
        self.ser.close()
        self.isConnected = False
        print("Leaving CLOSE, isConnected= "+str(self.isConnected))

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

    def reconnect(self):
        """Close and reconnect connection to Neato."""
        print("Entering RECONNECT()")
        self.log.debug("Reconnecting to Neato")
        print("Reconnecting to Neato")
        self.isConnected = False
        time.sleep(5)
        self.close()
        self.isConnected = self.connect()
        self.open()
        print("Leaving RECONNECT(),  isConnected = "+str(self.isConnected))

    def raw_write(self,msg):
        """Write message to serial and return output."""
        print("Entering RAW_WRITE(), msg = "+str(msg))
        out = ''
        if self.isConnected:
            inp = msg+"\n"
            self.ser.write(inp.encode('utf-8'))
            time.sleep(1)
            while self.ser.inWaiting() > 0:
                out += self.read_all(self.ser).decode('utf-8')
        print("Leaving RAW_WRITE()")
        return out

    def write(self, msg):
        """Write message to serial and return output. Handles Clean message."""
        print("Entering WRITE, msg = "+msg)
        self.log.debug("Message received for writing: "+msg)
        if self.isConnected:
            # wake up neato by sending something random
            try:
                print("Sending Wake-up msg.")
                out = self.raw_write("wake-up")
                # now send the real message
                out = self.raw_write(msg)
                if out is not '':
                    print("Leaving WRITE(), out = "+str(out)[:10])
                    return out
            except OSError as ex:
                self.log.error("Exception in 'write' method: "+str(ex))
                print("Exception in WRITE(): "+str(ex))
                print("Calling RECONNECT()")
                self.reconnect()
        else:
            print("Not connected in WRITE() - calling CONNECT()")
            self.isConnected = self.connect()

    def getError(self):
        """Return error message if available."""
        print("Entering GETERROR()")
        output = self.write("GetErr")
        if output is not None:
            outputsplit = output.split('\r\n')
            if len(outputsplit) == 3:
                err = outputsplit[1]
                if ' - ' in err:
                    errsplit = err.split(' - ')
                    print("Leaving GETERROR(), errsplit = "+str(errsplit))
                    return errsplit[0], errsplit[1]
            else:
                print("Leaving GETERROR(), return None since no output split.")
                return None
        else:
            print("Leaving GETERROR(), return None since Output is None.")
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
