"""Simple test class for testing relay."""
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
pins = [2, 3, 4, 17]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
print("All pins set to high")
while 1:
    inp = input("Enter pin number (2,3,4 or 17) and high or low: ")
    inpslit = inp.split(' ')
    to = GPIO.HIGH
    if inpslit[1] == 'low':
        to = GPIO.LOW
        GPIO.output(int(inpslit[0]), to)
