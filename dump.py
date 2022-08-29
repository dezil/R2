import constant
import logging
import time

from evdev import InputDevice, categorize, ecodes, list_devices


def dump_devices():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        print(device.path, device.name, device.phys)


def wait_for_device(name):
    while True:
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if device.name == name:
                return device
        time.sleep(5)


dump_devices()

logging.info("Connecting to devices...")

# creates object 'gamepad' to store the data
# you can call it whatever you like
gamepad = wait_for_device(constant.GAMEPAD)

# prints out device info at start
logging.info(gamepad)

logging.info("Running")

# evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():
    print(categorize(event))
