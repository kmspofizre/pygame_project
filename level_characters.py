import math
import os
import csv

import pygame

from game_settings import screen_width, screen_height, tile_size, screen
from sound import sound
from menu import end_menu

# путь csv уровней
level_0 = {'fon': './data/fon/first_level_fon.jpg',
           'surface': './levels/level0/level0_surface.csv',
           'cup': './levels/level0/level0_cup.csv',
           'bochki': './levels/level0/level0_bochki.csv',
           'player': './levels/level0/level0_player.csv',
           'enemy': './levels/level0/level0_enemy.csv'}
level_1 = {'fon': './data/fon/second_level_fon.png',
           'surface': './levels/level1/level1_surface.csv',
           'cup': './levels/level1/level1_cup.csv',
           'bochki': './levels/level1/level1_bochki.csv',
           'player': './levels/level1/level1_player.csv',
           'enemy': './levels/level1/level1_enemy.csv'}
level_2 = {'surface': './levels/level2/level2_surface.csv'}


archers = []  # список стрелков
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
main_character_group = pygame.sprite.Group()


def game_over():
    sound.play("game_over", 1, 0.1)
    main_character.hp = 1
    end_menu.menu()
    global running
    running = False


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
        raise FileNotFoundError(f"{fullname}")
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


'''УРОВЕНЬ'''


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
    def __init__(
            self, sheet, columns, rows, x, y,
            sprite_group=pygame.sprite.Group()
    ):
        super().__init__(sprite_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(
            0, 0, sheet.get_width() // columns, sheet.get_height() // rows
        )
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(
                    sheet.subsurface(
                        pygame.Rect(frame_location, self.rect.size)
                    )
                )

    def update(self, shift):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += shift


# класс фона
class Fon:
    def __init__(self):
        # self.first_level = pygame.image.load('./data/fon/.png').convert()
        self.second_level = pygame.image.load(
            './data/fon/second_level_fon.png'
        ).convert()
        # self.third_level = pygame.image.load('./data/fon/.png').convert()
        # self.four_level = pygame.image.load('./data/fon/.png').convert()

        #   self.first_level = pygame.transform.scale(self.first_level, (screen_width, screen_height))
        self.second_level = pygame.transform.scale(
            self.second_level, (screen_width, screen_height)
        )

    #   self.third_level = pygame.transform.scale(self.third_level, (screen_width, screen_height))
    #   self.four_level = pygame.transform.scale(self.four_level, (screen_width, screen_height))

    def draw(self, surface):
        # for stroki in range(tile_number_vertic):
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
    def __init__(self, level_data, surface, main_charaster):
        self.display_surface = surface
        self.screen_shift = 0

        player_layout = import_csv(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.finish = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, main_charaster)

        self.fon = Fon()

        surface_layout = import_csv(level_data['surface'])
        self.surface_sprites = self.create_tile_group(
            surface_layout, 'surface'
        )

        bochki_layout = import_csv(level_data['bochki'])
        self.bochki_sprites = self.create_tile_group(
            bochki_layout, 'bochki'
        )

        cup_layout = import_csv(level_data['cup'])
        self.cup_sprites = self.create_tile_group(
            cup_layout, 'cup'
        )

        enemy_layout = import_csv(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(
            enemy_layout, 'enemy'
        )

    # функция создания игрока из класса MainСharaster и точки выхода из уровня
    def player_setup(self, layout, main_charaster):
        for r_index, row in enumerate(layout):
            for c_index, znach in enumerate(row):
                x = c_index * tile_size
                y = r_index * tile_size
                if znach == '0':
                    self.player.add(main_charaster)
                if znach == '1':
                    finish_surface = load_image('./data/startfinish/finish.png', -1)
                    sprite = SurfaceTile(tile_size, x, y, finish_surface)
                    self.finish.add(sprite)

    # функция создания уровня из tile
    def create_tile_group(self, lay, type):
        sprite_group = pygame.sprite.Group()

        for r_index, row in enumerate(lay):
            for c_index, znach in enumerate(row):
                if znach != '-1':
                    x = c_index * tile_size
                    y = r_index * tile_size

                    if type == 'surface':
                        sprite = Surface(znach, x, y).return_sprite()

                    if type == 'bochki':
                        sprite = Barrels(znach, x, y).return_sprite()

                    if type == 'cup':
                        sprite = Coin(10, 1, x, y)
                        # surface_tile_list = import_cut_png('./data/cup/chirik.png')
                        # tile_surface = surface_tile_list[int(znach)]
                        # sprite = SurfaceTile(tile_size, x, y, tile_surface)

                    if type == 'enemy':
                        if znach == '0':
                            sprite = GroundEnemy(x, y - 50, 40)
                        if znach == '1':
                            continue

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

        self.enemy_sprites.update(self.screen_shift)
        self.enemy_sprites.draw(self.display_surface)


class Surface:
    tile_list = import_cut_png("./data/surface/surface.png")

    def __init__(self, val, x, y):
        self.tile_surface = Surface.tile_list[int(val)]
        self.sprite = SurfaceTile(tile_size, x, y, self.tile_surface)

    def return_sprite(self):
        return self.sprite


class Barrels:
    tile_list = import_cut_png("./data/bochki/bochka1.png")

    def __init__(self, val, x, y):
        self.tile_surface = Barrels.tile_list[int(val)]
        self.sprite = SurfaceTile(tile_size, x, y, self.tile_surface)

    def return_sprite(self):
        return self.sprite


class Coin(AnimatedSprite):
    sprite_sheet = load_image("./data/cup/coin.gif")

    def __init__(self, columns, rows, x, y):
        super().__init__(Coin.sprite_sheet, columns, rows, x, y)
        self.image = self.frames[self.cur_frame]

    def take_coin(self):
        self.kill()


'''ПЕРСОНАЖИ'''


class MainCharacter(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super().__init__(main_character_group)
        self.cur_frame = 0
        self.frames = self.cut_sheet(
            load_image("data/hero/lukang/idle_5_1.png", -1),
            5, 2, self.x, self.y
        )

        self.items = dict()
        self.coins = 0
        self.hp = 30

        # self.rect = pygame.Rect(2, 350, 20, 20)
        self.face = True
        self.moving = False
        self.rising = False
        self.jumping = False
        self.left = False
        self.right = False
        self.att = True
        self.standing = True  # флаг неподвижности
        self.last = 0
        self.rising_timer = 0
        self.iteration_counter = 0

    def cut_sheet(self, sheet, columns, rows, x, y):
        self.rect = pygame.Rect(
            x, y, sheet.get_width() // columns, sheet.get_height() // rows
        )
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(
                    sheet.subsurface(
                        pygame.Rect(frame_location, self.rect.size)
                    )
                )
        return frames

    def update(self, *args):
        self.iteration_counter += 1
        if self.iteration_counter % 3 == 0 or self.iteration_counter == 1:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        if pygame.sprite.spritecollideany(self, level.surface_sprites) \
                and self.check_ground():
            self.rising_timer = 0
            self.moving = True  # если находится на земле, то может прыгать
            self.jumping = False  # self.moving - флаг нахождения на платформе
            self.rising = False
        else:
            self.moving = False
        if pygame.sprite.spritecollide(self, level.cup_sprites, True):
            self.coins += 1
            print(self.coins)

        if not self.moving:  # если не на земле
            self.frames = self.cut_sheet(load_image("data/hero/lukang/jump_3_2.png"), 3, 2, self.rect.x,
                                         self.rect.y)
            if self.right:
                self.rect = self.rect.move(3, 0)
            if self.left:
                self.frames = self.cut_sheet(load_image("data/hero/lukang/jump_3_2_left.png"), 3, 2, self.rect.x,
                                             self.rect.y)
                self.rect = self.rect.move(-3, 0)
            if not self.rising:  # если не взлетает
                self.rect = self.rect.move(0, 1)  # падает
                self.moving = False  # анимация падения (или продолжение анимации прыжка)
            else:  # анимация взлета (ну или просто прыжка, если взлета нет)
                self.rect = self.rect.move(0, -5)  # взлетает до тех пор, пока self.rising_timer не ноль
                self.rising_timer -= 5  # rising_timer задается в функции jump
                if self.rising_timer == 0:
                    self.rising = False
        if self.moving:
            if self.right == self.left:
                if not self.jumping:
                    self.frames = self.cut_sheet(load_image("data/hero/lukang/idle_5_1.png"), 5, 1, self.rect.x,
                                                 self.rect.y)
                    self.standing = True
            elif self.left:
                self.frames = self.cut_sheet(
                    load_image("data/hero/lukang/move_5_2_left.png"), 5, 2, self.rect.x,
                    self.rect.y
                )
                self.rect = self.rect.move(-3, 0)  # анимация движения влево
                if not self.jumping:
                    self.standing = False
            elif self.right:
                self.frames = self.cut_sheet(load_image("data/hero/lukang/move_5_2.png"), 5, 2, self.rect.x,
                                             self.rect.y)
                self.rect = self.rect.move(3, 0)  # анимация движения вправо
                if not self.jumping:
                    self.standing = False
            if not self.att:  # проверка перезарядки атаки, если прошло больше 3 секунд с последней атаки
                now = pygame.time.get_ticks()  # атака перезаряжается
                if now - self.last >= 3000:
                    self.att = True

    def walking(self, direction):
        # определение направления движения
        if direction == pygame.K_a:
            self.left = True
        elif direction == pygame.K_d:
            self.right = True

    def stop_walking(self, direction):
        if direction == pygame.K_a:
            self.left = False
        elif direction == pygame.K_d:
            self.right = False

    def jump(self):

        # переменная jumping позволяет передвигаться в воздухе
        self.rising = True  # rising - взлет, rising_timer - таймер взлета, которое изменяется в update
        self.rising_timer += 200
        self.jumping = True
        self.moving = False
        self.standing = False
        self.rect = self.rect.move(0, -5)

    def get_damage(self):

        # получение урона от пуль и ходячих, если здоровье на нуле - игра окончена

        self.hp -= 1
        if self.hp == 0:
            game_over()

    def attack(self):
        if self.att and self.jumping:
            pass  # атака в прыжке (разработаю, когда будет анимация атаки в прыжке)
        elif self.att:  # гг производит атаку и перезаряжает ее
            for elem in enemies:
                elem.is_under_attack()  # проверка для каждого игрока находится ли он в поле действия атаки
            self.att = False
            self.last = pygame.time.get_ticks()

    def shoot(self, target):
        Shuriken(self.rect.x, self.rect.y, target[0], target[1], shurikens)

    def check_ground(self):
        for elem in level.surface_sprites:
            if pygame.sprite.spritecollideany(elem, main_character_group) \
                    and elem.rect.top == self.rect.bottom - 1:
                return True
        return False


class Platform(pygame.sprite.Sprite):

    # тестовое окружение

    def __init__(self, x, y, width, height):
        super().__init__(level.surface_sprites)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        pygame.draw.rect(
            self.image, pygame.Color('grey'), (0, 0, width, height)
        )
        self.rect = pygame.Rect(x, y, width, height)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(enemies)
        self.hp = 5

    def is_under_attack(self):
        if pygame.sprite.spritecollideany(self, main_character_group):  # получение урона от гг (функция attack)
            self.get_damage()

    def is_getting_shot(self):
        if pygame.sprite.spritecollideany(self, shurikens):
            self.get_damage()

    def get_damage(self):
        self.hp -= 1
        if self.hp == 0:
            self.kill()
            enemies.remove(self)
            if self in archers:
                archers.remove(self)


class Archer(Enemy):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("data/enemy/archer.png")
        self.rect = pygame.Rect(x, y, 100, 100)
        self.moving = False

    def update(self, *args):
        # проверка, стоит ли лучник на земле, если нет - падение
        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            self.moving = True
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)

    def shoot(self):
        # выстрел, при инициализации класса передаются координаты стрелка
        Bullet(self.rect.x, self.rect.y, main_character.rect.x, main_character.rect.y, bullets)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, group):
        super().__init__(group)
        self.frames = self.cut_sheet(load_image("data/enemy/bottle_12_2.png"), 12, 2, x, y)
        self.rect = pygame.Rect(x, y, 50, 50)
        self.cur_frame = 0
        # получение координат цели
        self.target_x = target_x
        self.target_y = target_y
        targets = [self.target_x, self.target_y]
        # нахождение расстояния между стрелком и целью
        paths = [abs(self.target_x - x), abs(self.target_y - y)]
        coords = [x, y]
        hypot = math.hypot(paths[0], paths[1])
        for_direction = [1, 1]
        # определение направления полета снаряда
        self.dx, self.dy = map(
            lambda i: for_direction[i] * 1
            if coords[i] - targets[i] < 0 else -1, range(2)
        )
        # сначала мы выясням, за сколько времени пуля пройдет гипотенузу
        # и потом присваиваем скорости по x и y значения: расстояние по x или y / время прохождения гипотенузы
        # 4 - скорость прохождения гипотенузы (выбрал сам)
        if paths[1] <= 10:
            self.vy = 0
        else:
            self.vy = math.ceil(paths[1] / (hypot / 4))
        if paths[0] <= 20:
            self.vx = 0
        else:
            self.vx = math.ceil(paths[0] / (hypot / 4))

    def cut_sheet(self, sheet, columns, rows, x, y):
        self.rect = pygame.Rect(
            x, y, sheet.get_width() // columns, sheet.get_height() // rows
        )
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(
                    sheet.subsurface(
                        pygame.Rect(frame_location, self.rect.size)
                    )
                )
        return frames

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        # пуля перемещается на произведение скорости и расстояния и при соприкосновении
        # с главным героем уменьшает его здоровье и пропадает

        self.rect = self.rect.move(self.vx * self.dx, self.vy * self.dy)
        if pygame.sprite.spritecollideany(self, main_character_group):
            main_character.get_damage()
            self.kill()
        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            self.kill()


class Shuriken(Bullet):
    def __init__(self, x, y, target_x, target_y, group):
        super().__init__(x, y, target_x, target_y, group)
        self.waiting = False
        self.touch_time = 0
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("white"),
                           (5, 5), 5)
        self.rect = pygame.Rect(x, y, 2 * 5, 2 * 5)

    def update(self):
        self.rect = self.rect.move(self.vx * self.dx, self.vy * self.dy)
        if pygame.sprite.spritecollideany(self, enemies):
            for elem in enemies:
                elem.is_getting_shot()  # поиск противника, в которого попали
            self.kill()
        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            self.kill()


class GroundEnemy(Enemy):
    def __init__(self, x, y, walking_range):
        super().__init__()
        self.frames = self.cut_sheet(
            load_image("data/enemy/idle_1_1.png"),
            1, 1, x, y
        )
        # начальная координата, которая является левой крайней точкой
        self.start_x = x
        self.rect = pygame.Rect(x, y, 50, 100)
        # конечная координата
        self.walking_range = walking_range
        self.moving = False
        self.attack = True
        self.cooldown = 3000
        self.last = 0
        self.direction = 1
        self.cur_frame = 0
        self.iteration_counter = 0
        self.attack_clock = pygame.time.Clock()

    def cut_sheet(self, sheet, columns, rows, x, y):
        self.rect = pygame.Rect(
            x, y, sheet.get_width() // columns, sheet.get_height() // rows
        )
        frames = []
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(
                    sheet.subsurface(
                        pygame.Rect(frame_location, self.rect.size)
                    )
                )
        return frames

    def update(self, *args):
        self.iteration_counter += 1
        if self.iteration_counter % 3 == 0 or self.iteration_counter == 1:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            # если стоит на земле, то запускается цикличный обход
            self.moving = True
            self.walking()
        else:
            self.moving = False
        if not self.moving:  # падение
            self.rect = self.rect.move(0, 1)
        if pygame.sprite.spritecollideany(self, main_character_group):
            if self.attack:
                main_character.get_damage()
                self.attack = False
                self.last = pygame.time.get_ticks()
            else:
                now = pygame.time.get_ticks()
                if now - self.last >= 3000:  # если с последней атаки прошло 3 и больше секунд
                    self.attack = True  # то можно атаковать снова
        if pygame.sprite.spritecollideany(self, shurikens):
            self.get_damage()

    def walking(self):
        # цикличное хождение влево-вправо от стартовой позиции до стартовая позиция + walking_range
        if self.rect.x + 1 > self.start_x + self.walking_range:
            self.frames = self.cut_sheet(
               pygame.transform.flip(
                   load_image("data/enemy/move_3_1.png"), True, False
               ),
               3, 1, self.rect.x, self.rect.y
            )
            self.direction = -1
        elif self.rect.x - 1 < self.start_x:
            self.frames = self.cut_sheet(
                load_image("data/enemy/move_3_1.png"),
                3, 1, self.rect.x, self.rect.y
            )
            self.direction = 1
        self.rect = self.rect.move(1 * self.direction, 0)


main_character = MainCharacter(2, 400)
level = Level(level_0, screen, main_character)
#level = Level(level_0, screen)

#main_character = MainCharacter(2, 400)
ar = Archer(100, 250)
enemies.add(ar)
archers.append(ar)