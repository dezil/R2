import os
import random

from loguru import logger
from pygame import mixer


class Audio(object):

    def __init__(self, path, volume):
        self.path = path

        mixer.init()
        mixer.music.set_volume(float(volume))

    def play_random_sound(self, category):
        category_path = os.path.join(self.path, category)
        file_path = os.path.join(category_path, random.choice(os.listdir(category_path)))
        self.play_sound(file_path)

    def play_sound(self, filename):
        logger.debug("Loading {file}", file=filename)
        mixer.music.load(filename)
        logger.info("Playing {file}", file=filename)
        mixer.music.play()
