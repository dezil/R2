import logging
import os
import random

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
        logging.debug("Loading %s", filename)
        mixer.music.load(filename)
        logging.info("Playing %s", filename)
        mixer.music.play()
