import constant

from loguru import logger
from managers import AudioManager
from threading import Event, Thread


class Autonomous(object):

    def __init__(self, audio_manager: AudioManager):
        self.audio_manager = audio_manager
        self.event: Event = Event()
        self.event.set()
        self.thread: Thread | None = None

    def start(self):
        if not self.event.is_set():
            return

        logger.info("Starting Automation")
        self.event.clear()
        Thread(target=self.run, name="Autonomous Thread").start()

    def stop(self):
        if self.event.is_set():
            return

        logger.info("Stopping Automation")
        self.event.set()

    def toggle(self):
        if self.event.is_set():
            self.start()
        else:
            self.stop()

    def run(self):
        self.audio_manager.play_random_sound(constant.AUTO_CATEGORY)
        while not self.event.wait(constant.AUTO_INTERVAL):
            self.audio_manager.play_random_sound(constant.AUTO_CATEGORY)
