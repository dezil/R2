from buildhat import Motor, MotorPair
from loguru import logger


class MotorManager(object):

    def __init__(self):
        self.periscope_motor: Motor | None = None
        self.rotation_motor: MotorPair | None = None

    def init(self, periscope_motor: Motor, rotation_motor: MotorPair):
        self.periscope_motor = periscope_motor
        self.rotation_motor = rotation_motor

    def run_periscope(self, degrees: int, threshold: int, speed: int):
        if self.periscope_motor is None:
            return

        if self.periscope_motor.get_position() >= threshold:
            logger.trace("Starting Periscope ({} @ {})", degrees, -speed)
            self.periscope_motor.run_for_degrees(degrees, -speed, False)
        else:
            logger.trace("Starting Periscope ({} @ {})", degrees, speed)
            self.periscope_motor.run_for_degrees(degrees, speed, False)

    def run_rotation(self, speed: int):
        if self.rotation_motor is None:
            return

        if speed == 0:
            logger.trace("Stopping Rotation")
            self.rotation_motor.stop()
        else:
            logger.trace("Starting Rotation ({})", str(speed))
            self.rotation_motor.start(speed)