import constant
import os
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
            # A Button
            if event.button == 0:
                self.audio_manager.play_random_sound("scream")
                logger.trace("A Button")

            # B Button
            if event.button == 1:
                self.audio_manager.play_random_sound("misc")
                logger.trace("B Button")

            # X Button
            if event.button == 2:
                self.audio_manager.play_random_sound("music")
                logger.trace("X Button")

            # Y button
            if event.button == 3:
                self.audio_manager.play_random_sound("alarm")
                logger.trace("Y Button")

            # Left Bumper
            if event.button == 4:
                logger.trace("Left Bumper")
                self.motor_manager.run_door('left')

            # Right Bumper
            if event.button == 5:
                logger.trace("Right Bumper")
                self.motor_manager.run_door('right')

            # Back button
            if event.button == 6:
                logger.trace("back Button")

            # Start Button
            if event.button == 7:
                logger.trace("Start Button")

            # Left stick click
            if event.button == 8:
                logger.trace("L stick click")

            # Right stick click
            if event.button == 9:
                self.audio_manager.play_sound(os.path.join(constant.AUDIO_PATH, "R2BDAY1.mp3"))
                logger.trace("R stick Click")

            # guide button
            if event.button == 10:
                logger.trace("Guide Button")

            # R1 Button
            if event.button == 11:
                self.autonomous.toggle()
            else:
                self.autonomous.stop()

            # Cross Button
            if event.button == 14:
                logger.trace("Cross Button")
                self.audio_manager.play_random_sound("scream")

        # Dpad Up / Down | Left / Right
        if event.type == pygame.JOYHATMOTION:
            self.audio_manager.play_dpad(event)
            
        if event.type == pygame.JOYAXISMOTION:
            # Left Stick | Left / Right
            if event.axis == 0:
                self.motor_manager.stickYaw = event.value
                self.motor_manager.set_tracks()
            # Left Stick | Up / Down
            elif event.axis == 1:
                self.motor_manager.stickPitch = event.value
                self.motor_manager.set_tracks()
            # Trigger Left
            elif event.axis == 2:
                if event.value >= 0.5:
                    self.motor_manager.motor_lock = False
                    logger.trace("Motor Unlocked")
                elif event.value <= -0.5:
                    self.motor_manager.motor_lock = True
                    logger.trace("Motor Locked")
            # Right Stick | Left / Right
            elif event.axis == 3:
                self.motor_manager.run_rotation(
                    constant.ROTATION_THRESHOLD,
                    max(-100, min(100, int(util.scale(event.value, (0.0, 1.0), (0, 100))))),
                    constant.ROTATION_INVERT
                )
            # Right Trigger
            elif event.axis == 5:
                if event.value >= 0.5:
                    self.audio_manager.alternate_sound = True
                elif event.value <= -0.5:
                    self.audio_manager.alternate_sound = False

    def list_devices(self):
        logger.info("Devices:")
        for device in self.joysticks:
            logger.info("- #{} {} ({})", device.get_instance_id(), device.get_name(), device.get_guid())
