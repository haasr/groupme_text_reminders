from time import sleep

import RPi.GPIO as gpio
import atexit

atexit.register(gpio.cleanup) # Properly dispose of gpio resources

RED_PIN    = 18
YELLOW_PIN = 23
GREEN_PIN  = 24

blinking = False

gpio.setmode(gpio.BCM)
gpio.setup(RED_PIN, gpio.OUT)
gpio.setup(YELLOW_PIN, gpio.OUT)
gpio.setup(GREEN_PIN, gpio.OUT)


# Blink pattern to indicate that messages were successfully retreived:
def blink_successful_retrieval():
    global blinking
    if blinking: # Wait for current use of LEDs to finish
        sleep(.8)

    blinking = True

    gpio.output(YELLOW_PIN, gpio.LOW)
    sleep(.8)
    gpio.output(YELLOW_PIN, gpio.HIGH)

    blinking = False


# Blink pattern to indicate that messages were not successfully retreived:
def blink_unsuccessful_retrieval():
    global blinking
    if blinking: # Wait for current use of LEDs to finish
        sleep(.8)

    blinking = True

    gpio.output(RED_PIN, gpio.LOW)
    sleep(.8)
    gpio.output(RED_PIN, gpio.HIGH)

    blinking = False


# Blink pattern to indicate that an new message was received:
def blink_incoming():
    global blinking
    if blinking: # Wait for current use of LEDs to finish
        sleep(.8)

    blinking = True

    gpio.output(GREEN_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(GREEN_PIN, gpio.HIGH)
    sleep(.1)
    gpio.output(GREEN_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(GREEN_PIN, gpio.HIGH)
    sleep(.1)
    gpio.output(GREEN_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(GREEN_PIN, gpio.HIGH)

    blinking = False
    

# Blink pattern to indicate that an outgoing message was sent:
def blink_outgoing():
    global blinking
    if blinking: # Wait for current use of LEDs to finish
        sleep(.8)

    blinking = True

    gpio.output(YELLOW_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(YELLOW_PIN, gpio.HIGH)
    sleep(.1)
    gpio.output(YELLOW_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(YELLOW_PIN, gpio.HIGH)
    sleep(.1)
    gpio.output(YELLOW_PIN, gpio.LOW)
    sleep(.2)
    gpio.output(YELLOW_PIN, gpio.HIGH)

    blinking = False


# Blink pattern to indicate that a task notification will be displayed:
def blink_notification():
    global blinking
    if blinking: # Wait for current use of LEDs to finish
        sleep(.8)

    blinking = True
    
    for i in range(0, 3):
        gpio.output(RED_PIN, gpio.LOW)
        sleep(.1)
        gpio.output(RED_PIN, gpio.HIGH)
        gpio.output(YELLOW_PIN, gpio.LOW)
        sleep(.1)
        gpio.output(YELLOW_PIN, gpio.HIGH)
        gpio.output(GREEN_PIN, gpio.LOW)
        sleep(.1)
        gpio.output(GREEN_PIN, gpio.HIGH)

    blinking = False


def blink_unsuccessful_send():
    global blinking
    if blinking:
        sleep(.8)

    blinking = True

    for i in range(0, 8):
        gpio.output(RED_PIN, gpio.LOW)
        sleep(.1)
        gpio.output(RED_PIN, gpio.HIGH)
