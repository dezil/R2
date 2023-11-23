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
        self.light_manager = light_manager
        self.rotation_motor: Motor | None = None

        self.arm_motor: Motor | None = None
        self.arm_open: bool = False
        self.arm_sequence: int = 0
        
        self.door_left_motor: Motor | None = None
        self.door_left_open: bool = False
        self.door_right_motor: Motor | None = None
        self.door_right_open: bool = False
                
        self.track_lock: bool = True
        self.track_left: VESC | None = None
        self.track_left_throttle_last: float = 0
        self.track_right: VESC | None = None
        self.track_right_throttle_last: float = 0

        self.stick_pitch: float = 0
        self.stick_yaw: float = 0

    def init(self):
        if platform.system() == "Windows":
            logger.warning("Unsupported Platform: {}", platform.system())
            return

        while True:
            try:
                if constant.ARM_ENABLED:
                    self.arm_motor = Motor(constant.ARM_MOTOR)
                if constant.DOOR_LEFT_ENABLED:
                    self.door_left_motor = Motor(constant.DOOR_LEFT_MOTOR)
                if constant.DOOR_RIGHT_ENABLED:
                    self.door_right_motor = Motor(constant.DOOR_RIGHT_MOTOR)
                if constant.ROTATION_ENABLED:
                    self.rotation_motor = Motor(constant.ROTATION_MOTOR)
                    self.rotation_motor.plimit(1)
            except BuildHATError as e:
                logger.error(e)
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

    def run_arm_sequence(self):
        if self.arm_sequence == 0:
            self.run_door_right(True)
        elif self.arm_sequence == 1:
            self.run_arm(True)
        elif self.arm_sequence == 2:
            self.run_arm(True)
        elif self.arm_sequence == 3:
            self.run_door_right(True)

        if self.arm_sequence < 3:
            self.arm_sequence += 1
        else:
            self.arm_sequence = 0

    def run_arm(self, blocking=False):
        if self.arm_motor is None:
            return

        if self.arm_open:
            degrees = constant.ARM_DEGREES_CLOSE
        else:
            degrees = constant.ARM_DEGREES_OPEN

        logger.info("Arm changing from {} to {} position: (degrees {})", 
            "opened" if self.arm_open else "closed",
            "opened" if not self.arm_open else "closed",
            degrees
        )

        self.arm_motor.run_for_degrees(degrees, constant.ARM_SPEED, blocking)
        self.arm_open = not self.arm_open

    def run_door_left(self, blocking=False):
        if self.door_left_motor is None:
            return

        if self.door_left_open:
            degrees = constant.DOOR_LEFT_DEGREES_CLOSE
        else:
            degrees = constant.DOOR_LEFT_DEGREES_OPEN

        logger.info("Door Left changing from {} to {} position: (degrees {})", 
            "opened" if self.door_left_open else "closed",
            "opened" if not self.door_left_open else "closed",
            degrees
        )

        self.door_left_motor.run_for_degrees(degrees, constant.DOOR_LEFT_SPEED, blocking)
        self.door_left_open = not self.door_left_open
    
    def run_door_right(self, blocking=False):
        if self.door_right_motor is None:
            return

        if self.door_right_open:
            degrees = constant.DOOR_RIGHT_DEGREES_CLOSE
        else:
            degrees = constant.DOOR_RIGHT_DEGREES_OPEN

        logger.info("Right Door changing from {} to {} position: (degrees {})", 
            "opened" if self.door_right_open else "closed",
            "opened" if not self.door_right_open else "closed",
            degrees
        )

        self.door_right_motor.run_for_degrees(degrees, constant.DOOR_RIGHT_SPEED, blocking)
        self.door_right_open = not self.door_right_open

    def run_rotation(self, threshold: int, speed: int, invert: bool = False):
        if self.rotation_motor is None:
            return

        if invert:
            if speed > 0:
                speed = -speed
            elif speed < 0:
                speed = abs(speed)

        if -threshold <= speed <= threshold:
            logger.trace("Stopping Rotation")
            self.rotation_motor.stop()
        else:
            logger.trace("Starting Rotation ({})", str(speed))
            self.rotation_motor.start(speed)

    def set_tracks(self): 
        if not constant.TRACK_ENABLED:
            return
        
        if self.track_lock:
            if self.track_left_throttle_last != 0 or self.track_right_throttle_last != 0:
                self.track_left.set_duty_cycle(0)
                self.track_right.set_duty_cycle(0)

                self.track_left_throttle_last = 0
                self.track_right_throttle_last = 0
            return
        
        throttle = max(0, abs(self.stick_pitch) - 0.05) 
        yaw = max(0, abs(self.stick_yaw) - 0.05) 

        if self.stick_pitch > 0:
            throttle = throttle * - 1
            
        if self.stick_yaw < 0:
            yaw = yaw * - 1

        throttle_left = min(throttle + yaw, 1)
        throttle_right = min(throttle - yaw, 1)

        rpm_left = max(-constant.TRACK_MAX_SPEED, min(constant.TRACK_MAX_SPEED, int(util.scale(throttle_left, (0.0, 1.0), (0, constant.TRACK_MAX_SPEED)))))
        rpm_right = max(-constant.TRACK_MAX_SPEED, min(constant.TRACK_MAX_SPEED, int(util.scale(throttle_right, (0.0, 1.0), (0, constant.TRACK_MAX_SPEED)))))

        self.track_left.set_rpm(rpm_left)
        self.track_right.set_rpm(rpm_right)

        self.track_left_throttle_last = throttle_left
        self.track_right_throttle_last = throttle_right