import os
import sys
import math

import pygame

from sound import sound
from menu import end_menu
from level_characters import level


def load_image(name, color_key=None):
    fullname = os.path.join('', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def game_over():
    sound.play("game_over", 1, 0.1)
    main_character.hp = 1
    end_menu.menu()
    global running
    running = False





main_character = MainCharacter(2, 400)
ar = Archer(100, 250)
archers = [ar]  # список стрелков
