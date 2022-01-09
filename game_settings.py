import sqlite3

import pygame

# настройка размера экрана и размера tile
tile_number_vertic = 12
tile_size = 64

fps = 25

clock1 = pygame.time.Clock()

SHOOTING_EVENT = pygame.USEREVENT + 1

screen_height = tile_number_vertic * tile_size
screen_width = 1200
screen = pygame.display.set_mode((screen_width, screen_height))

connection = sqlite3.connect('data\score.db')

surface_color = "#7ec0ee"