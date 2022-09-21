import asyncio
import constant

from loguru import logger
from managers import AudioManager


class Autonomous(object):

    def __init__(self, audio_manager: AudioManager):
        self.audio_manager = audio_manager
        self.task: asyncio.Task | None = None

    def start(self):
        if self.task is not None:
            return

        self.task = asyncio.create_task(self.run())

    def stop(self):
        if self.task is None:
            return

        self.task.cancel()
        self.task = None

    def toggle(self):
        if self.task is None:
            logger.info("Starting Automation")
            self.start()
        else:
            logger.info("Stopping Automation")
            self.stop()

    async def run(self):
        while self.task is not None and not self.task.cancelled():
            self.audio_manager.play_random_sound(constant.AUTO_CATEGORY)
            await asyncio.sleep(constant.AUTO_INTERVAL)
