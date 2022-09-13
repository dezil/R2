import constant
import os
import platform
os.environ["LOGURU_LEVEL"] = constant.LOG_LEVEL
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
if platform.system() != "Windows":
    os.environ["SDL_VIDEODRIVER"] = "dummy"

import asyncio
import pygame
import sys

from managers import AudioManager, InputManager, LightManager, MotorManager
from autonomous import Autonomous
from loguru import logger

audio_manager = AudioManager()
autonomous = Autonomous(audio_manager)
light_manager = LightManager()
motor_manager = MotorManager(light_manager)
input_manager = InputManager(audio_manager, autonomous, motor_manager)


async def main():
    logger.info("Starting...")

    try:
        pygame.init()
        input_manager.init()
        light_manager.init()
        motor_manager.init()

        if len(sys.argv) == 1 and sys.argv[0] == "dump":
            input_manager.list_devices()
            return

        logger.info("Started")
        while True:
            event = pygame.event.wait(1000)
            if event.type == pygame.NOEVENT:
                continue

            logger.trace("{} Event", pygame.event.event_name(event.type))

            if event.type == pygame.QUIT:
                break

            input_manager.handle(event)

        logger.info("Stopping...")
    except KeyboardInterrupt as ex:
        logger.warning("KeyboardInterrupt, Stopping...")
    except Exception as ex:
        logger.error(ex)
    finally:
        autonomous.stop()
        light_manager.quit()
        motor_manager.quit()
        input_manager.quit()
        pygame.quit()

    logger.info("Stopped")


if __name__ == "__main__":
    asyncio.run(main())
