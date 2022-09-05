import constant
import pygame

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

            # iOS Button
            if event.button == 307:
                self.audio_manager.play_random_sound("alarms")

            # Triangle Button
            if event.button == 308:
                self.audio_manager.play_random_sound("misc")

            # A Button
            if event.button == 305:
                self.audio_manager.play_random_sound("scream")

            # X Button
            if event.button == 315:
                self.audio_manager.play_random_sound("music")

        if event.type == pygame.JOYAXISMOTION:
            # Full Up
            if event.axis == 1 and event.value <= -1.0:
                self.motor_manager.run_periscope(
                    constant.PERISCOPE_DEGREES,
                    constant.PERISCOPE_THRESHOLD,
                    constant.PERISCOPE_SPEED
                )

            # Full Down
            if event.axis == 1 and event.value >= 1.0:
                self.autonomous.toggle()

            # Full Left
            if event.axis == 0 and event.value <= -1.0:
                self.motor_manager.run_rotation(constant.ROTATION_SPEED_HIGH)

            # Partial Left
            if event.axis == 0 and -0.63 >= event.value >= -0.79:
                self.motor_manager.run_rotation(constant.ROTATION_SPEED_MEDIUM)

            # Partial Left
            if event.axis == 0 and -0.30 >= event.value >= -0.36:
                self.motor_manager.run_rotation(constant.ROTATION_SPEED_LOW)

            # Full Right
            if event.axis == 0 and event.value >= 1.0:
                self.motor_manager.run_rotation(-constant.ROTATION_SPEED_HIGH)

            # Partial Right
            if event.axis == 0 and 0.63 <= event.value <= 0.79:
                self.motor_manager.run_rotation(-constant.ROTATION_SPEED_MEDIUM)

            # Partial Right
            if event.axis == 0 and 0.30 <= event.value <= 0.36:
                self.motor_manager.run_rotation(-constant.ROTATION_SPEED_LOW)

    def quit(self):
        self.joysticks = None
        pygame.joystick.quit()

    def list_devices(self):
        logger.info("Devices:")
        for device in self.joysticks:
            logger.info("- #{} {} ({})", device.get_instance_id(), device.get_name(), device.get_guid())