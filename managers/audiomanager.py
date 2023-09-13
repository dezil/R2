import constant
import os
import pygame
import random

from loguru import logger


class AudioManager(object):

    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.music.set_volume(float(constant.AUDIO_VOLUME))
        self.alternate_sound = False

    def play_random_sound(self, category):
        category_path = os.path.join(constant.AUDIO_PATH, category)
        file_path = os.path.join(category_path, random.choice(os.listdir(category_path)))
        self.play_sound(file_path)

    def play_sound(self, filename):
        logger.trace("Loading {}", filename)
        pygame.mixer.music.load(filename)
        logger.info("Playing {}", filename)
        pygame.mixer.music.play()

    def play_dpad(self, event: pygame.event):
        x, y = event.value
        sound_filename = ""

        if x == 0 and y == 0:
            return

        if x == 0 and y == 1:
            sound_filename = "GHOSTBUSTERS.mp3" if not self.alternate_sound else "sounds_WOLFWSTL.mp3"
        elif x == 0 and y == -1:
            sound_filename = "LOTR_ISENGARD.mp3" if not self.alternate_sound else "LEIA.mp3"
        elif x == 1 and y == 0:
            sound_filename = "LOTR_THE_SHIRE.mp3" if not self.alternate_sound else "R2BDAY1.mp3"
        elif x == -1 and y == 0:
            sound_filename = "LOTR_YSNP.mp3" if not self.alternate_sound else "R2PLAYME.mp3"

        self.play_sound(os.path.join(constant.AUDIO_PATH, sound_filename))