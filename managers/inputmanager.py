import constant
import pygame
import util

from autonomous import Autonomous
from loguru import logger
from managers import AudioManager, MotorManager


class InputManager(object):

    def __init__(self, audio_manager: AudioManager, autonomous: Autonomous, motor_manager: MotorManager):
        self.audio_manager = audio_manager
        self.autonomous = autonomous
        self.motor_manager = motor_manager
        self.joysticks = {}

    def init(self):
        pygame.joystick.init()

    def quit(self):
        self.joysticks = None
        pygame.joystick.quit()

    def handle(self, event: pygame.event):
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            self.joysticks[joystick.get_instance_id()] = joystick
            logger.info("Joystick {} connected", joystick.get_instance_id())

        if event.type == pygame.JOYDEVICEREMOVED:
            del self.joysticks[event.instance_id]
            logger.info("Joystick {} disconnected", event.instance_id)

        if event.type == pygame.JOYBUTTONUP:
            self.autonomous.stop()

            # Select Button
            if event.button == 0:
                logger.trace("Select Button")

            # L3 Button
            if event.button == 1:
                logger.trace("L3 Button")

            # R3 Button
            if event.button == 2:
                logger.trace("R3 Button")

            # Start Button
            if event.button == 3:
                logger.trace("Start Button")

            # Up Button
            if event.button == 4:
                logger.trace("Up Button")
                self.motor_manager.run_periscope(
                    constant.PERISCOPE_DEGREES,
                    constant.PERISCOPE_THRESHOLD,
                    constant.PERISCOPE_SPEED,
                    constant.PERISCOPE_DEGREES_MINIMUM,
                    constant.PERISCOPE_DEGREES_MAXIMUM
                )

            # Right Button
            if event.button == 5:
                logger.trace("Right Button")

            # Down Button
            if event.button == 6:
                logger.trace("Down Button")

            # Left Button
            if event.button == 7:
                logger.trace("Left Button")

            # L2 Button
            if event.button == 8:
                logger.trace("L2 Button")

            # R2 Button
            if event.button == 9:
                logger.trace("R2 Button")

            # L1 Button
            if event.button == 10:
                logger.trace("L1 Button")

            # R1 Button
            if event.button == 11:
                logger.trace("R1 Button")

            # Triangle Button
            if event.button == 12:
                logger.trace("Triangle Button")
                self.audio_manager.play_random_sound("alarms")

            # Circle Button
            if event.button == 13:
                logger.trace("Circle Button")
                self.audio_manager.play_random_sound("misc")

            # Cross Button
            if event.button == 14:
                logger.trace("Cross Button")
                self.audio_manager.play_random_sound("scream")

            # Square Button
            if event.button == 15:
                logger.trace("Square Button")
                self.audio_manager.play_random_sound("music")

        if event.type == pygame.JOYAXISMOTION:
            # Full Up
            if event.axis == 1 and event.value <= -1.0:
                pass

            # Full Down
            if event.axis == 1 and event.value >= 1.0:
                self.autonomous.toggle()

            # Left / Right
            if event.axis == 0:
                self.motor_manager.run_rotation(
                    constant.ROTATION_THRESHOLD,
                    max(-100, min(100, util.scale(event.value, (0.0, 1.0), (0, 100)))),
                    constant.ROTATION_INVERT
                )

    def list_devices(self):
        logger.info("Devices:")
        for device in self.joysticks:
            logger.info("- #{} {} ({})", device.get_instance_id(), device.get_name(), device.get_guid())
