import constant
import platform
import time
import util

from pyvesc import VESC
from buildhat import BuildHATError, Motor
from loguru import logger
from managers import LightManager


class MotorManager(object):

    def __init__(self, light_manager: LightManager):
        self.left_door_motor: Motor | None = None
        self.right_door_motor: Motor | None = None

        self.light_manager = light_manager
        self.periscope_motor: Motor | None = None
        self.rotation_motor: Motor | None = None
        self.track_left: VESC | None = None
        self.track_right: VESC | None = None
        self.stickPitch: float = 0
        self.stickYaw: float = 0
        self.motor_lock: bool = True
        self.motor_left_throttle_last: float = 0
        self.motor_right_throttle_last: float = 0

    def init(self):
        if platform.system() == "Windows":
            logger.warning("Unsupported Platform: {}", platform.system())
            return

        while True:
            try:
                if constant.DOOR_LEFT_ENABLED:
                    self.left_door_motor = Motor(constant.DOOR_LEFT_MOTOR)
                if constant.DOOR_RIGHT_ENABLED:
                    self.right_door_motor = Motor(constant.DOOR_RIGHT_MOTOR)
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

    def run_door(self, door: str):
        if self.left_door_motor is None or self.right_door_motor is None:
            return

        degrees_minimum: int = 0
        degrees_maximum: int = 0
        threshold: int = 0
        speed: int = 0
        motor: Motor | None = None

        if door == "left":
            degrees_minimum = constant.DOOR_LEFT_DEGREES_MINIMUM
            degrees_maximum = constant.DOOR_LEFT_DEGREES_MAXIMUM
            threshold = constant.DOOR_LEFT_THRESHOLD
            speed = constant.DOOR_LEFT_SPEED
            motor = self.left_door_motor
        elif door == "right":
            degrees_minimum = constant.DOOR_RIGHT_DEGREES_MINIMUM
            degrees_maximum = constant.DOOR_RIGHT_DEGREES_MAXIMUM
            threshold = constant.DOOR_RIGHT_THRESHOLD
            speed = constant.DOOR_RIGHT_SPEED
            motor = self.right_door_motor
        else:
            return

        position = motor.get_position()
        if position >= threshold:
            degrees = position - degrees_minimum
            logger.info("Starting Door (from {}, to {}, at {})", position, degrees, -speed)
            motor.run_for_degrees(degrees, -speed, False)
        else:
            degrees = degrees_maximum - (position - degrees_minimum)
            logger.info("Starting Door (from {}, to {}, at {})", position, degrees, speed)
            motor.run_for_degrees(degrees, speed, False)

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
        
        if self.motor_lock:
            if self.motor_left_throttle_last != 0 or self.motor_right_throttle_last != 0:
                self.track_left.set_duty_cycle(0)
                self.track_right.set_duty_cycle(0)

                self.motor_left_throttle_last = 0
                self.motor_right_throttle_last = 0
            return
        
        throttle = max(0, abs(self.stickPitch) - 0.05) 
        yaw = max(0, abs(self.stickYaw) - 0.05) 

        if self.stickPitch > 0:
            throttle = throttle * - 1
            
        if self.stickYaw < 0:
            yaw = yaw * - 1

        throttle_left = min(throttle + yaw, 1)
        throttle_right = min(throttle - yaw, 1)

        rpm_left = max(-constant.TRACK_MAX_SPEED, min(constant.TRACK_MAX_SPEED, int(util.scale(throttle_left, (0.0, 1.0), (0, constant.TRACK_MAX_SPEED)))))
        rpm_right = max(-constant.TRACK_MAX_SPEED, min(constant.TRACK_MAX_SPEED, int(util.scale(throttle_right, (0.0, 1.0), (0, constant.TRACK_MAX_SPEED)))))

        self.track_left.set_rpm(rpm_left)
        self.track_right.set_rpm(rpm_right)

        self.motor_left_throttle_last = throttle_left
        self.motor_right_throttle_last = throttle_right