import sys

import pygame

pygame.init()


# класс музыки и звуков
class Sound(object):
    # инициализация  класса
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        self.sounds = {}
        self.load_sounds()

    # загрузка списка музыки и звуков из каталога
    def load_sounds(self):
        try:
            self.sounds['game1'] = pygame.mixer.Sound(
                'audio/music1.wav'
            )
            self.sounds['game2'] = pygame.mixer.Sound(
                'audio/music2.wav'
            )
            self.sounds['game3'] = pygame.mixer.Sound(
                'audio/music3.wav'
            )
            self.sounds['game4'] = pygame.mixer.Sound(
                'audio/music4.wav'
            )
            self.sounds['game_over'] = pygame.mixer.Sound(
                'audio/game_over.wav'
            )
            self.sounds['Lymez'] = pygame.mixer.Sound(
                'audio/Lymez-Margaritas_at_Dawn.wav'
            )
        except Exception:
            print('Не найдены файлы музыки и звуков !')
            sys.exit()

    # воспроизведение звуков
    def play(self, name, loops, volume):
        self.sounds[name].play(loops=loops)
        self.sounds[name].set_volume(volume)

    # остановка воспроизведения звуков
    def stop(self, name):
        self.sounds[name].stop()


sound = Sound()
