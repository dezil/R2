import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import asyncio
import constant
import logging
import time

from audio import Audio
from buildhat import Motor
from evdev import InputDevice, categorize, ecodes, list_devices

logging.basicConfig(filename="latest.log", encoding="utf-8", level=logging.DEBUG)
audio = Audio(constant.AUDIO_PATH, constant.AUDIO_VOLUME)


def get_device(name, blocking=False):
    while True:
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if device.name == name:
                return device
        if blocking:
            time.sleep(5)
        else:
            return None


def run_periscope(motor):
    if motor.get_position() >= 700:
        logging.info("Running Periscope: Down")
        motor.run_for_degrees(720, -25, False)
    else:
        logging.info("Running Periscope: Up")
        motor.run_for_degrees(720, 25, False)


def run_rotate(motors, speed):
    logging.info("Running Rotate: " + str(speed))
    for motor in motors:
        if speed == 0:
            motor.stop()
        else:
            motor.start(speed)


async def main():
    logging.info("Connecting to devices...")

    # creates object 'gamepad' to store the data
    gamepad = get_device(constant.GAMEPAD, True)
    motor_a = Motor("A")
    motor_c = Motor("C")
    motor_d = Motor("D")

    logging.info("Running")

    # loop and filter by event code and logging.info the mapped label
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:  # Key
            if event.value == 1:  # Key Down
                if event.code == 307:  # iOS
                    logging.info("Event: iOS")
                    audio.play_random_sound("alarms")
                elif event.code == 308:  # Triangle
                    logging.info("Event: Triangle")
                    audio.play_random_sound("misc")
                elif event.code == 305:  # A
                    logging.info("Event: A")
                    audio.play_random_sound("scream")
                elif event.code == 304:  # X
                    logging.info("Event: X")
                    audio.play_random_sound("music")
                elif event.code == 315:  # Start
                    logging.info("Event: Start")
        if event.type == ecodes.EV_ABS:  # Axis
            if event.code == 0:  # X Axis
                logging.info("Event X Axis: " + str(event.value))
                if event.value == 0:  # Full Up
                    run_periscope(motor_a)

                if event.value == 255:  # Full Down
                    logging.info("BOTTOM")

            elif event.code == 1:  # Y Axis
                logging.info("Event Y Axis: " + str(event.value))
                if event.value == 0:  # Full Right
                    run_rotate([motor_c, motor_d], 40)
                elif 1 <= event.value <= 42:  # Partial Right
                    run_rotate([motor_c, motor_d], 30)
                elif 43 <= event.value <= 127:  # Partial Right
                    run_rotate([motor_c, motor_d], 20)
                elif event.value == 128:  # Stop
                    run_rotate([motor_c, motor_d], 0)
                elif 129 <= event.value <= 213:  # Partial Left
                    run_rotate([motor_c, motor_d], -20)
                elif 214 <= event.value <= 254:  # Partial Left
                    run_rotate([motor_c, motor_d], -30)
                elif event.value == 255:  # Full Left
                    run_rotate([motor_c, motor_d], -40)


if __name__ == "__main__":
    asyncio.run(main())
