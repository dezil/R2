import constant

from buildhat import Motor
from loguru import logger


class MotorManager(object):

    def __init__(self):
        self.periscope_motor: Motor | None = None
        self.rotation_motor: Motor | None = None

    def init(self):
        try:
            self.periscope_motor = Motor(constant.PERISCOPE_MOTOR)
            self.rotation_motor = Motor(constant.ROTATION_MOTOR)
            self.rotation_motor.plimit(1)
        except Exception as ex:
            logger.error(ex)

    def quit(self):
        self.run_rotation(0, 0)

    def run_periscope(self, degrees_minimum: int, degrees_maximum: int, threshold: int, speed: int):
        if self.periscope_motor is None:
            return

        position = self.periscope_motor.get_position()
        if position >= threshold:
            degrees = position - degrees_minimum
            logger.info("Starting Periscope (from {}, to {}, at {})", position, degrees, -speed)
            self.periscope_motor.run_for_degrees(degrees, -speed, False)
        else:
            degrees = degrees_maximum - (position - degrees_minimum)
            logger.info("Starting Periscope (from {}, to {}, at {})", position, degrees, speed)
            self.periscope_motor.run_for_degrees(degrees, speed, False)

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
