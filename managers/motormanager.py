import constant
import platform
import time

from pyvesc import VESC
from buildhat import BuildHATError, Motor
from loguru import logger
from managers import LightManager


class MotorManager(object):

    def __init__(self, light_manager: LightManager):
        self.light_manager = light_manager
        self.periscope_motor: Motor | None = None
        self.rotation_motor: Motor | None = None
        self.track_left: VESC | None = None
        self.track_right: VESC | None = None
        self.stickPitch: float = 0
        self.stickYaw: float = 0

    def init(self):
        if platform.system() == "Windows":
            logger.warning("Unsupported Platform: {}", platform.system())
            return

        while True:
            try:
                if constant.PERISCOPE_ENABLED:
                    self.periscope_motor = Motor(constant.PERISCOPE_MOTOR)
                if constant.ROTATION_ENABLED:
                    self.rotation_motor = Motor(constant.ROTATION_MOTOR)
                    self.rotation_motor.plimit(1)
            except BuildHATError:
                logger.debug("Waiting for BuildHAT...")
                time.sleep(1)
                continue
            except Exception as ex:
                logger.error(ex)

            break

        if constant.TRACK_ENABLED:
            self.track_left = VESC(constant.TRACK_TTY_LEFT)
            self.track_right = VESC(constant.TRACK_TTY_RIGHT)

    def quit(self):
        self.run_rotation(0, 0)
        self.track_left.stop_heartbeat()
        self.track_right.stop_heartbeat()

    def run_periscope(self, degrees_minimum: int, degrees_maximum: int, threshold: int, speed: int):
        if self.periscope_motor is None:
            return

        position = self.periscope_motor.get_position()
        if position >= threshold:
            degrees = position - degrees_minimum
            logger.info("Starting Periscope (from {}, to {}, at {})", position, degrees, -speed)
            self.periscope_motor.run_for_degrees(degrees, -speed, False)
            self.light_manager.run_periscope(False)
        else:
            degrees = degrees_maximum - (position - degrees_minimum)
            logger.info("Starting Periscope (from {}, to {}, at {})", position, degrees, speed)
            self.periscope_motor.run_for_degrees(degrees, speed, False)
            self.light_manager.run_periscope(True)

    def run_rotation(self, threshold: int, speed: int, invert: bool = False):
        if self.rotation_motor is None:
            return

        if invert:
            if speed > 0:
                speed = -speed
            elif speed < 0:
                speed = abs(speed)

        if -threshold <= speed <= threshold:
            logger.info("Stopping Rotation")
            self.rotation_motor.stop()
        else:
            logger.info("Starting Rotation ({})", str(speed))
            self.rotation_motor.start(speed)

    def set_tracks(self): 
        if not constant.TRACK_ENABLED:
            return
        
        throttle = max(0, abs(self.stickPitch) - 0.05) 
        yaw = max(0, abs(self.stickYaw) - 0.05) 

        if self.stickPitch > 0:
            throttle = throttle * - 1
            
        if self.stickYaw < 0:
            yaw = yaw * - 1

        throttle_left = min(throttle + yaw, 1)
        throttle_right = min(throttle - yaw, 1)

        self.track_left.set_duty_cycle(throttle_left)
        self.track_right.set_duty_cycle(throttle_right)