import csv
import pygame
import os
import sys
import random

tile_number_vertic = 12
tile_size = 64

screen_height = tile_number_vertic * tile_size
screen_width = 1200

# путь csv уровней
level_0 = {'surface': './levels/level0/level0_surface.csv',
           'cup': './levels/level0/level0_cup.csv',
           'bochki': './levels/level0/level0_bochki.csv'}
level_1 = {'surface': './levels/level0/level1_surface.csv'}
level_2 = {'surface': './levels/level0/level2_surface.csv'}


# функция импортирования файла описания уровня csv
def import_csv(path):
    surface_spisok = []
    with open(path) as filein:
        level = csv.reader(filein, delimiter=',')
        for row in level:
            surface_spisok.append(list(row))
        return surface_spisok


# функция создания списка поверхностей tile из одного файла png
def import_cut_png(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_x = int(surface.get_size()[0] / tile_size)
    tile_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    for row in range(tile_y):
        for col in range(tile_x):
            x = col * tile_size
            y = row * tile_size
            new = pygame.Surface((tile_size, tile_size), flags=pygame.SRCALPHA)
            new.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new)
    return cut_tiles


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


# родительский класс tile
class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, shift):
        self.rect.x += shift


# класс tile поверхности
class SurfaceTile(Tile):
    def __init__(self, size, x, y, surface):
        super().__init__(size, x, y)
        self.image = surface


# анимированый tile
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(pygame.sprite.Group())
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self, shift):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += shift

# класс фона
class Fon():
    def __init__(self):
       # self.first_level = pygame.image.load('./data/fon/.png').convert()
        self.second_level = pygame.image.load('./data/fon/second_level_fon.png').convert()
       # self.third_level = pygame.image.load('./data/fon/.png').convert()
       # self.four_level = pygame.image.load('./data/fon/.png').convert()

     #   self.first_level = pygame.transform.scale(self.first_level, (screen_width, screen_height))
        self.second_level = pygame.transform.scale(self.second_level, (screen_width, screen_height))
     #   self.third_level = pygame.transform.scale(self.third_level, (screen_width, screen_height))
     #   self.four_level = pygame.transform.scale(self.four_level, (screen_width, screen_height))

    def draw(self, surface):
        #for stroki in range(tile_number_vertic):
         #   rasmer_tile = stroki * tile_size
         #   if row < 3:
         #       surface.blit(self.first_level, (0, rasmer_tile))
         #   elif row >= 3 and row <= 6:
         #       surface.blit(self.second_level, (0, rasmer_tile))
         #   elif row > 6:
         #       surface.blit(self.third_level, (0, rasmer_tile))
         #   else:
         #       surface.blit(self.four_level, (0, rasmer_tile))
        surface.blit(self.second_level, (0, 0))

# класс уровня
class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.screen_shift = 0

        self.fon = Fon()

        surface_layout = import_csv(level_data['surface'])
        self.surface_sprites = self.create_tile_group(surface_layout, 'surface')

        bochki_layout = import_csv(level_data['bochki'])
        self.bochki_sprites = self.create_tile_group(bochki_layout, 'bochki')

        cup_layout = import_csv(level_data['cup'])
        self.cup_sprites = self.create_tile_group(cup_layout, 'cup')

    # функция создания уровня из tile
    def create_tile_group(self, lay, type):
        sprite_group = pygame.sprite.Group()

        for r_index, row in enumerate(lay):
            for c_index, znach in enumerate(row):
                if znach != '-1':
                    x = c_index * tile_size
                    y = r_index * tile_size

                    if type == 'surface':
                        surface_tile_list = import_cut_png('./data/surface/surface.png')
                        tile_surface = surface_tile_list[int(znach)]
                        sprite = SurfaceTile(tile_size, x, y, tile_surface)

                    if type == 'bochki':
                        surface_tile_list = import_cut_png('./data/bochki/bochka1.png')
                        tile_surface = surface_tile_list[int(znach)]
                        sprite = SurfaceTile(tile_size, x, y, tile_surface)

                    if type == 'cup':
                        sprite = AnimatedSprite(load_image("./data/cup/coin.gif"), 10, 1, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    # функция сдвига tile-ов в зависимости от движения игрока (камера)
    def sdvig_x(self, direction_x):
        if direction_x < 0:
            self.screen_shift = 5
        elif direction_x > 0:
            self.screen_shift = -5
        else:
            self.screen_shift = 0

    # функция обновления tile уровня на экране
    def create(self):
        self.fon.draw(self.display_surface)

        self.surface_sprites.update(self.screen_shift)
        self.surface_sprites.draw(self.display_surface)

        self.bochki_sprites.update(self.screen_shift)
        self.bochki_sprites.draw(self.display_surface)

        self.cup_sprites.update(self.screen_shift)
        self.cup_sprites.draw(self.display_surface)

