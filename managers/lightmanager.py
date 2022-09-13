import constant
import platform

from gpiozero import LED
from loguru import logger


class LightManager(object):

    def __init__(self):
        self.periscope_led: LED | None = None

    def init(self):
        if platform.system() == "Windows":
            logger.warning("Unsupported Platform: {}", platform.system())
            return

        self.periscope_led = LED(constant.PERISCOPE_LED)

    def quit(self):
        self.run_periscope(False)

    def run_periscope(self, state: bool = None):
        if self.periscope_led is None:
            return

        if state is None:
            self.periscope_led.toggle()
            return

        if state:
            self.periscope_led.on()
        else:
            self.periscope_led.off()
