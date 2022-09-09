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
        except Exception as ex:
            logger.error(ex)

    def quit(self):
        self.run_rotation(0, 0)

    def run_periscope(self, degrees: int, threshold: int, speed: int):
        if self.periscope_motor is None:
            return

        if self.periscope_motor.get_position() >= threshold:
            logger.info("Starting Periscope ({} @ {})", degrees, -speed)
            self.periscope_motor.run_for_degrees(degrees, -speed, False)
        else:
            logger.info("Starting Periscope ({} @ {})", degrees, speed)
            self.periscope_motor.run_for_degrees(degrees, speed, False)

    def run_rotation(self, threshold: int, speed: int):
        if self.rotation_motor is None:
            return

        if -threshold <= speed <= threshold:
            logger.info("Stopping Rotation")
            self.rotation_motor.stop()
        else:
            logger.info("Starting Rotation ({})", str(speed))
            self.rotation_motor.start(speed)
