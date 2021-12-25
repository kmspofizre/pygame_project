import pygame

# класс музыки и звуков
class Sound(object):
    # инициализация класса
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        self.sounds = {}
        self.load_sounds()

    # загрузка списка музыки и звуков из каталога
    def load_sounds(self):
        self.sounds['game1'] = pygame.mixer.Sound('audio\\music1.mp3')
        self.sounds['game2'] = pygame.mixer.Sound('audio\\music2.mp3')

    # воспроизведение звуков
    def play(self, name, loops, volume):
        self.sounds[name].play(loops=loops)
        self.sounds[name].set_volume(volume)

    # остановка воспроизведения звуков
    def stop(self, name):
        self.sounds[name].stop()