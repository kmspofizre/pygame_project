import os
import sys
import math
import pygame
import csv

# загрузка настроек игры, уровней и различных классов
#from game_settings import *
#from sound import Sound
#from cursor import Cursor

surface_color = "#7ec0ee"

# путь csv уровней
level_0 = {'surface': './levels/level0/level0_surface.csv',
           'cup': './levels/level0/level0_cup.csv',
           'bochki': './levels/level0/level0_bochki.csv',
           'enemy': './levels/level0/level0_enemy.csv'}
level_1 = {'surface': './levels/level1/level1_surface.csv',
           'cup': './levels/level1/level1_cup.csv',
           'bochki': './levels/level1/level1_bochki.csv',
           'enemy': './levels/level1/level1_enemy.csv'}
level_2 = {'surface': './levels/level2/level2_surface.csv'}

tile_number_vertic = 12
tile_size = 64

screen_height = tile_number_vertic * tile_size
screen_width = 1200

enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
main_character_group = pygame.sprite.Group()


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


class Cursor(pygame.sprite.Sprite):
    # инициализация класса
    def __init__(self, group):
        super().__init__(group)
        self.image = load_image("data\cursor\cursor.gif")
        self.rect = self.image.get_rect()


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
        self.sounds['game3'] = pygame.mixer.Sound('audio\\music3.mp3')
        self.sounds['game4'] = pygame.mixer.Sound('audio\\music4.mp3')

    # воспроизведение звуков
    def play(self, name, loops, volume):
        self.sounds[name].play(loops=loops)
        self.sounds[name].set_volume(volume)

    # остановка воспроизведения звуков
    def stop(self, name):
        self.sounds[name].stop()


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

        enemy_layout = import_csv(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')

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
                        #surface_tile_list = import_cut_png('./data/cup/chirik.png')
                        #tile_surface = surface_tile_list[int(znach)]
                        #sprite = SurfaceTile(tile_size, x, y, tile_surface)

                    if type == 'enemy':
                        if znach == '0':
                            surface_tile_list = import_cut_png('./data/enemy/enemy.gif')
                            tile_surface = surface_tile_list[0]
                            sprite = GroundEnemy(x, y, 40, tile_surface)
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


class MainCharacter(pygame.sprite.Sprite):
    def __init__(self, sheet, x, y, rows, columns):
        super().__init__(main_character_group)

        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

        self.items = dict()
        self.hp = 50

        self.moving = False
        self.rising = False
        self.jumping = False
        self.left = False
        self.right = False
        self.att = True
        self.last = 0
        self.rising_timer = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        if pygame.sprite.spritecollideany(self, level.surface_sprites):  # если находится на земле, то может прыгать
            self.moving = True                               # self.moving - флаг нахождения на платформе
            self.jumping = False
            self.rising = False
        else:
            self.moving = False
        if not self.moving:                                  # если не на земле
            if not self.rising:                              # если не взлетает
                self.rect = self.rect.move(0, 3)             # падает
                self.moving = False
            else:
                self.rect = self.rect.move(0, -5)            # взлетает до тех пор, пока self.rising_timer не ноль
                self.rising_timer -= 5                       # rising_timer задается в функции jump
                if self.rising_timer == 0:
                    self.rising = False
        if self.left and self.right:
            pass
        elif self.left:
            self.rect = self.rect.move(-1, 0)
            # камера
            level.sdvig_x(-1)
        elif self.right:
            self.rect = self.rect.move(1, 0)
            # камера
            level.sdvig_x(1)
        # камера
        else:
            level.sdvig_x(0)

        if not self.att:  # проверка перезарядки атаки, если прошло больше 3 секунд с последней атаки
            now = pygame.time.get_ticks()  # атака перезаряжается
            if now - self.last >= 3000:
                self.att = True

    def walking(self, direction):
        # определение направления движения
        if direction == pygame.K_LEFT:
            self.left = True
        elif direction == pygame.K_RIGHT:
            self.right = True

    def stop_walking(self, direction):
        if direction == pygame.K_LEFT:
            self.left = False
        elif direction == pygame.K_RIGHT:
            self.right = False

    def jump(self):

        # переменная jumping позволяет передвигаться в воздухе
        self.rising = True  # rising - взлет, rising_timer - таймер взлета, которое изменяется в update
        self.rising_timer += 100
        self.jumping = True
        self.moving = False
        self.rect = self.rect.move(0, -5)

    def get_damage(self):

        # получение урона от пуль и ходячих, если здоровье на нуле, то игра окончена

        self.hp -= 1
        if self.hp == 0:
            game_over()

    def attack(self):
        if self.att and self.jumping:
            pass  # атака в прыжке (разработаю, когда будет анимация атаки в прыжке)
        elif self.att:  # гг производит атаку и перезаряжает ее
            for elem in enemies_sp:
                elem.is_under_attack()  # проверка для каждого игрока находится ли он в поле действия атаки
            self.att = False
            self.last = pygame.time.get_ticks()

    def shoot(self, target):
        Shuriken(self.rect.x, self.rect.y, target[0], target[1], shurikens)




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
            enemies_sp.remove(self)
            if self in archers:
                archers.remove(self)


class Archer(Enemy):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, 20, 20))
        self.rect = pygame.Rect(x, y, 20, 20)
        self.moving = False

    def update(self, *args):

        # проверка, стоит ли лучник на земле, если нет - то падение

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
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"),
                           (5, 5), 5)
        self.rect = pygame.Rect(x, y, 2 * 5, 2 * 5)
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
        self.dx, self.dy = map(lambda i: for_direction[i] * 1 if coords[i] - targets[i] < 0 else -1, range(2))
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

    def update(self):
        # пуля перемещается на произведение скорости и расстояния и при соприкосновении
        # с главным героем уменьшает его здоровье и пропадает

        self.rect = self.rect.move(self.vx * self.dx, self.vy * self.dy)
        if pygame.sprite.spritecollideany(self, main_character_group):
            main_character.get_damage()
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
            for elem in enemies_sp:
                elem.is_getting_shot()  # поиск противника, в которого попали
            self.kill()


class GroundEnemy(Enemy):
    def __init__(self, x, y, walking_range, surface):
        super().__init__()
        self.image = surface
        #self.image = pygame.Surface((64, 64), pygame.SRCALPHA, 32)
        #pygame.draw.rect(self.image, pygame.Color('pink'), (0, 0, 64, 64))
        self.start_x = x
        self.rect = pygame.Rect(x, y, 64, 64)
        self.walking_range = walking_range
        self.moving = False
        self.direction = 1

    def update(self, shift):
        #if pygame.sprite.spritecollideany(self, platforms):
        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            self.moving = True
            self.walking()
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)

        self.rect.x += shift

    def walking(self):
        if self.rect.x + 1 > self.start_x + self.walking_range:
            self.direction = -1
        elif self.rect.x - 1 < self.start_x:
            self.direction = 1
        self.rect = self.rect.move(1 * self.direction, 0)


class Menu:
    def __init__(self, menu_item):
        self.menu_item = menu_item

    def render(self, screen, font, num_menu_item):
        font = pygame.font.Font('fonts/Asessorc.otf', 30)
        screen.blit(font.render('Copyright 2021-2022', 1, 'red'), (450, 700))

        font = pygame.font.Font('fonts/Acsiomasupershockc.otf', 50)
        for i in self.menu_item:
            if num_menu_item == i[5]:
                screen.blit(font.render(i[2], 1, i[4]), (i[0], i[1] - 70))
            else:
                screen.blit(font.render(i[2], 1, i[3]), (i[0], i[1] - 70))

    def menu(self):
        pygame.mouse.set_visible(True)
        sound.play('game2', 10, 0.3)
        active_menu = True
        pygame.key.set_repeat(0, 0)
        font_menu = pygame.font.Font('fonts/Acsiomasupershockc.otf', 50)
        menu_item = 0
        while active_menu:
            screen.fill((0, 100, 200))
            mouse_coords = pygame.mouse.get_pos()

            if pygame.mouse.get_focused():
                cursor.draw(screen)

            for i in self.menu_item:
                if mouse_coords[0] > i[0] and mouse_coords[0] < i[0] + 155 and mouse_coords[1] > i[1] and mouse_coords[1] < i[1] + 50:
                    menu_item = i[5]

            self.render(screen, font_menu, menu_item)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if menu_item == 0:
                            sound.stop('game2')
                            active_menu = False
                        if menu_item == 1:
                            sys.exit()
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_UP:
                        if menu_item > 0:
                            menu_item -= 1
                    if event.key == pygame.K_DOWN:
                        if menu_item < len(self.menu_item) - 1:
                            menu_item += 1
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_item == 0:
                        sound.stop('game2')
                        active_menu = False
                    if menu_item == 1:
                        print('rules')
                    if menu_item == 2:
                        print('best')
                    if menu_item == 3:
                        sys.exit()

            pygame.display.update()


def game_over():
    global running
    running = False


def start_level():
    sound.play('game4', 10, 0.3)

    running = True
    while running:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                running = False
                sound.stop('game4')
               # pygame.quit()
               # sys.exit()
            if event.type == SHOOTING_EVENT:
                for j in range(len(archers)):
                    archers[j].shoot()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and main_character.moving:
                    main_character.jump()
                if main_character.moving or main_character.jumping:
                    main_character.walking(event.key)
            if event.type == pygame.KEYUP:
                main_character.stop_walking(event.key)
            if event.type == pygame.MOUSEMOTION:
                cur.rect = event.pos

            # обработчик камеры
         #   if keys[pygame.K_RIGHT]:
          #      level.sdvig_x(1)
          #  elif keys[pygame.K_LEFT]:
          #      level.sdvig_x(-1)
          #  else:
          #      level.sdvig_x(0)

        # вызов метода обновления экрана
        level.create()

        # обработчик курсора
        if pygame.mouse.get_focused():
            cursor.draw(screen)

        main_character.update()
        # enemies.update(0)
        shurikens.update()
        bullets.update()
        bullets.draw(screen)
        main_character_group.draw(screen)
        # enemies.draw(screen)
        clock1.tick(fps)
        # pygame.display.flip()
        pygame.display.update()


if __name__ == '__main__':
    level_change = 0

    pygame.init()

    screen = pygame.display.set_mode((screen_width, screen_height))

    SHOOTING_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SHOOTING_EVENT, 3000)
    clock1 = pygame.time.Clock()
    fps = 25

    # инициализация звука и музыки
    sound = Sound()

    # инициализация курсора pygame.display.set_caption('Приключение Лю Кэнга')
    pygame.mouse.set_visible(False)
    cursor = pygame.sprite.Group()
    cur = Cursor(cursor)

    #создание меню
    menu_items = [(520, 210, u'Game', 'yellow', 'red', 0),
                  (530, 280, u'Rules', 'yellow', 'green', 1),
                  (540, 350, u'Best', 'yellow', 'brown', 2),
                  (550, 420, u'Quit', 'yellow', 'black', 3)]
    game = Menu(menu_items)


    running = True
    while running:
        game.menu()
        # инициализация уровня
        if level_change == 0:
            level = Level(level_0, screen)
        elif level_change == 1:
            level = Level(level_1, screen)

        #main_character = MainCharacter()
        main_character = MainCharacter(load_image("./data/hero/lukang.gif"), 2, 400, 1, 6)
        ar = Archer(100, 250)
        archers = [ar]  # список стрелков
        # we = GroundEnemy(150, 350, 40)
        # enemies_sp = [we, ar]  # список врагов

        start_level()
        level_change = 1

pygame.quit()