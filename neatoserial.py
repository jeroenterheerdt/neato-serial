"""Serial interface for Neato."""
from config import settings
import serial
import os
import time


class NeatoSerial:
    """Serial interface to Neato."""

    def __init__(self):
        """Initialize serial connection to Neato."""
        devices = settings['serial']['serial_device'].split(',')
        for dev in devices:
            try:
                self.ser = serial.Serial(dev, 115200,
                                         serial.EIGHTBITS, serial.PARITY_NONE,
                                         serial.STOPBITS_ONE,
                                         settings['serial']['timeout_seconds'])
                self.open()
            except:
                print("Could not connect to device "+dev+". Trying next device.")

    def open(self):
        """Open serial port and flush the input."""
        self.ser.isOpen()
        self.ser.flushInput()

    def close(self):
        """Close serial port."""
        self.ser.close()

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

    def write(self, msg):
        """Write message to serial and return output."""
        inp = msg+"\n"
        self.ser.write(inp.encode('utf-8'))
        if msg == "Clean":
            # toggle usb
            if settings['serial']['usb_switch_mode'] == 'direct':
                # disable and re-enable usb ports to trigger clean
                os.system('sudo ./hub-ctrl -h 0 -P 2 -p 0 ; sleep 1; '
                          + 'sudo ./hub-ctrl -h 0 -P 2 -p 1 ')
                if settings['serial']['reboot_after_usb_switch']:
                    os.system('sudo reboot')
            else:
                # use relais to temporarily disconnect neato to trigger clean
                to_do = True
        out = ''
        # let's wait one second before reading output
        time.sleep(1)
        while self.ser.inWaiting() > 0:
            out += self.read_all(self.ser).decode('utf-8')
            if out != '':
                return out

    def getBatteryLevel(self):
        """Return battery level."""
        return int(self.getCharger()["FuelPercent"])

    def getChargingActive(self):
        """Return true if device is currently charging."""
        return bool(int(self.getCharger()["ChargingActive"]))

    def getExtPwrPresent(self):
        """Return true if device is currently docked."""
        return bool(int(self.getCharger()["ExtPwrPresent"]))

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
        return int(self.getMotors()["Vacuum_RPM"])

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
    ns.open()
    print("Enter commands. Enter 'exit' to quit")
    while 1:
        inp = input("? ")
        if inp == 'exit':
            ns.close()
            exit()
        else:
            print(">> "+ns.write(inp))
