import csv
import pygame
from game_settings import *


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

# класс уровня
class Level:
	def __init__(self, level_data, surface):
		self.display_surface = surface
		self.screen_shift = 0

		surface_layout = import_csv(level_data['surface'])
		self.surface_sprites = self.create_tile_group(surface_layout, 'surface')

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
		self.surface_sprites.update(self.screen_shift)
		self.surface_sprites.draw(self.display_surface)
