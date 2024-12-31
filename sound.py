import enum
import pygame

class Samples(enum.StrEnum):
    STARTUP = "woosh-motion.mp3"
    TIMER_START = "game-start.mp3"
    TIMER_EXPIRED1 = "level-up.mp3"
    TIMER_EXPIRED2 = "item-pick-up.mp3"
    TIMER_TICK = "tick.mp3"
    TIMER_STOP = "down-fart.mp3"
    SHUTDOWN = "gameboy-pluck.mp3"
    ABRUPT_SHUTDOWN = "kid-bye.mp3"


# uses pygame mixer to play sound samples as requested
class Sound:
    def __init__(self, volume=0.1):
        self.sound = None
        self.volume = volume

    def play(self, sample: Samples):
        if self.sound:
            self.sound.stop()
        # init mixer if not already
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sound = pygame.mixer.Sound("sound/" + sample.value)
        self.sound.set_volume(self.volume)
        self.sound.play()