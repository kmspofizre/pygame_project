import math
import os
import csv

import pygame.time

import game_settings
from game_settings import *
from menu import menu, end_menu, result_level
from cursor import cursor, cur
from sound import sound
from interface import inventory, draw_interface

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
level_2 = {'fon': './data/fon/level_fon_3.jpg',
           'surface': './levels/level2/level2_surface.csv',
           'cup': './levels/level2/level2_cup.csv',
           'bochki': './levels/level2/level2_bochki.csv',
           'player': './levels/level2/level2_player.csv',
           'enemy': './levels/level2/level2_enemy.csv'}

archers = []  # список стрелков

# группы отображаемых спрайтов
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
main_character_group = pygame.sprite.Group()


# Обновление кадра
def start_level():
    sound.play('game4', 10, 0.3)

    draw_inventory = False
    hold_left_btn = False
    global running
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            mouse_btns = pygame.mouse.get_pressed()
            if event.type == SHOOTING_EVENT:
                for j in range(len(archers)):
                    archers[j].shoot()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and main_character.moving:
                    main_character.jump()
                main_character.walking(event.key)
                if event.key == pygame.K_f:
                    if main_character.left or main_character.right or\
                            main_character.rising or main_character.jumping:
                        main_character.is_attacking = False
                    else:
                        if pygame.time.get_ticks() - game_settings.time >= 1500:
                            main_character.attack()
                            game_settings.time = pygame.time.get_ticks()
                if event.key == pygame.K_1:
                    inventory.add_item("coin")
            if event.type == pygame.KEYUP:
                main_character.stop_walking(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pygame.mouse.get_pos()
                    if not (x < 64 and y < 64):
                        main_character.shoot((x, y))
                    if x < 64 and y < 64:
                        draw_inventory = True
                        main_character.inventory_opened = True
                    if x < 10 or y < 10 or x > 440 or y > 230:
                        draw_inventory = False
                        main_character.inventory_opened = False
                if event.button == 3:
                    main_character.shoot(event.pos)
            if draw_inventory:
                if mouse_btns[0] and not hold_left_btn:
                    inventory.set_start_cell(pygame.mouse.get_pos())
                    hold_left_btn = True
                if hold_left_btn and not mouse_btns[0]:
                    inventory.set_end_cell(pygame.mouse.get_pos())
                    hold_left_btn = False
            if event.type == pygame.MOUSEMOTION:
                cur.rect = event.pos

        # вызов метода обновления экрана
        level.update()

      #  main_character.update()
        shurikens.update()
        shurikens.draw(screen)
        bullets.update()
        bullets.draw(screen)
        for archer in archers:
            archer.update()
        enemies.draw(screen)
      #  main_character_group.draw(screen)
        draw_interface(main_character.hp)
        if draw_inventory:
            inventory.draw_inventory()
        clock1.tick(fps)
        # обработчик курсора
        if pygame.mouse.get_focused():
            cursor.draw(screen)
        pygame.display.update()


# Окончание игры при смерти героя
def game_over():
    sound.play("game_over", 1, 0.1)
    main_character.hp = 1
    end_menu.show_menu()
    ar.kill()
    archers.clear()
    main_character.kill()
    for sprite in enemies:
        sprite.kill()
    enemies.clear(screen, screen)
    global running
    running = False


# функция импортирования файла описания уровня  csv
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


# Преобразование -png или -jpg файла в объект
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

    # разбитие спрайт-сета на спрайты
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

    # Смена спрайта
    def update(self, shift):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect.x += shift


# класс фона
class Fon:
    def __init__(self, fon):
        self.level_fon = pygame.image.load(fon).convert()
        self.level_fon = pygame.transform.scale(
            self.level_fon, (screen_width, screen_height)
        )

    def draw(self, surface):
        surface.blit(self.level_fon, (0, 0))


# класс уровня
class Level:
    def __init__(self, level_data, surface, main_character):
        self.display_surface = surface
        self.screen_shift = 0

        # Импортирование данных из -csv файлов
        player_layout = import_csv(level_data['player'])
        self.main_character = main_character
        self.player = pygame.sprite.GroupSingle()
        self.finish = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, self.main_character)

        fon = level_data['fon']
        self.fon = Fon(fon)

        surface_layout = import_csv(level_data['surface'])
        self.surface_sprites = self.create_tile_group(
            surface_layout, 'surface'
        )
        self.left_ones = self.create_left(
            surface_layout, 'surface'
        )

        self.right_ones = self.create_right(surface_layout, 'surface')

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

    # функция создания игрока из класса MainСharacter и точки выхода из уровня
    def player_setup(self, layout, main_charaster):
        for r_index, row in enumerate(layout):
            for c_index, znach in enumerate(row):
                x = c_index * tile_size
                y = r_index * tile_size
                if znach == '0':
                    self.player.add(main_charaster)
                if znach == '1':
                    try:
                        finish_surface = load_image(
                            './data/startfinish/finish.png', -1
                        )
                    except Exception:
                        print("отсутствует спрайты карты")
                    sprite = SurfaceTile(tile_size, x, y, finish_surface)
                    self.finish.add(sprite)

    def create_left(self, lay, type):
        sprite_group = pygame.sprite.Group()

        for r_index, row in enumerate(lay):
            for c_index, znach in enumerate(row):
                if znach != '-1':
                    x = c_index * tile_size
                    y = r_index * tile_size

                    if type == 'surface':
                        if znach in ('3', '6'):
                            sprite = Surface(znach, x, y).return_sprite()
                            sprite_group.add(sprite)

        return sprite_group

    def create_right(self, lay, type):
        sprite_group = pygame.sprite.Group()

        for r_index, row in enumerate(lay):
            for c_index, znach in enumerate(row):
                if znach != '-1':
                    x = c_index * tile_size
                    y = r_index * tile_size

                    if type == 'surface':
                        if znach in ('5', '8'):
                            sprite = Surface(znach, x, y).return_sprite()
                            sprite_group.add(sprite)

        return sprite_group

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

                    if type == 'enemy':
                        if znach == '0':
                            sprite = GroundEnemy(x, y - 50, 40, 0)
                        if znach == '1':
                            continue

                    sprite_group.add(sprite)

        return sprite_group

    # функция сдвига tile-ов в зависимости от движения игрока (камера)
    def sdvig_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        if player_x < screen_width / 2 and direction_x < 0:
            self.screen_shift = 10
        elif player_x > screen_width - (screen_width / 2) and direction_x > 0:
            self.screen_shift = -10
        else:
            self.screen_shift = 0

    # Камера
    def check_camera(self):
        right_rect = pygame.rect.Rect(game_settings.screen_width, 0, 1, game_settings.screen_height)
        left_rect = pygame.rect.Rect(0, 0, 1, game_settings.screen_height)

        if right_rect.colliderect(main_character.rect):
            for elem in bullets:
                elem.rect.x -= 500
            for elem in enemies:
                if elem.__class__ == GroundEnemy:
                    elem.start_x -= 500
            self.fon.draw(self.display_surface)
            self.surface_sprites.update(-500)
            self.bochki_sprites.update(-500)
            self.cup_sprites.update(-500)
            self.enemy_sprites.update(-500)
            self.right_ones.update(-500)
            self.left_ones.update(-500)

            self.surface_sprites.draw(self.display_surface)
            self.bochki_sprites.draw(self.display_surface)
            self.cup_sprites.draw(self.display_surface)
            self.player.draw(self.display_surface)

            main_character.rect.x -= 500
            ar.update_sdvig_x(-500)
            self.finish.update(-500)

        if left_rect.colliderect(main_character.rect):
            for elem in bullets:
                elem.rect.x += 500
            for elem in enemies:
                if elem.__class__ == GroundEnemy:
                    elem.start_x += 500
            self.fon.draw(self.display_surface)
            self.surface_sprites.update(500)
            self.bochki_sprites.update(500)
            self.cup_sprites.update(500)
            self.enemy_sprites.update(500)
            self.right_ones.update(500)
            self.left_ones.update(500)

            self.surface_sprites.draw(self.display_surface)
            self.bochki_sprites.draw(self.display_surface)
            self.cup_sprites.draw(self.display_surface)
            self.player.draw(self.display_surface)

            main_character.rect.x += 500
            ar.update_sdvig_x(500)
            self.finish.update(500)

    # Проаерка на достижение финиша
    def check_finish(self):
        if pygame.sprite.spritecollide(main_character, self.finish, False):
            # удаление лишних врагов с экрана
            for sprite in self.enemy_sprites:
                # if isinstance(sprite, GroundEnemy):
                sprite.kill()
            sound.stop('game4')
            result_level(
                main_character.coins,
                main_character.hp,
                main_character.enemy_kill
            )
            global running
            running = False

    # функция обновления tile уровня на экране
    def update(self):
        self.fon.draw(self.display_surface)

        self.surface_sprites.update(self.screen_shift)
        self.surface_sprites.draw(self.display_surface)

        self.bochki_sprites.update(self.screen_shift)
        self.bochki_sprites.draw(self.display_surface)

        self.cup_sprites.update(self.screen_shift)
        self.cup_sprites.draw(self.display_surface)

        self.enemy_sprites.update(self.screen_shift)
        # self.enemy_sprites.draw(self.display_surface)

        ar.update_sdvig_x(self.screen_shift)

        self.player.update()
        #self.sdvig_x()
        self.check_camera()
        self.player.draw(self.display_surface)
        self.finish.update(self.screen_shift)
        self.finish.draw(self.display_surface)

        self.check_finish()


# Классы для функции create_tile_group класса Level
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
    try:
        sprite_sheet = load_image("./data/cup/coin.gif")
    except Exception:
        print("отсутствует анимация монеты")

    def __init__(self, columns, rows, x, y):
        super().__init__(Coin.sprite_sheet, columns, rows, x, y)
        self.image = self.frames[self.cur_frame]

    def take_coin(self):
        self.kill()


'''ПЕРСОНАЖИ'''


# Главный герой
class MainCharacter(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super().__init__(main_character_group)
        self.cur_frame = 0
        try:
            self.frames = self.cut_sheet(
                load_image("data/hero/lukang/idle_5_1.png", -1),
                5, 2, self.x, self.y
            )
        except Exception:
            print("отсутствует анимация бездействия перснажа")

        self.items = dict()
        self.inventory_opened = False
        self.coins = 0
        self.hp = 10
        self.enemy_kill = 0

        # вектор движения героя
        self.direction = pygame.math.Vector2(0, 0)

        self.is_attacking = False
        self.moving = False
        self.rising = False
        self.jumping = False
        self.left = False
        self.right = False
        self.reloading = False
        self.standing = True  # флаг неподвижности
        self.attack_timer = 0
        self.last = 0
        self.rising_timer = 0
        self.iteration_counter = 0
        self.shuriken = 5

    # обработка спрайт-сетов
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
        if self.iteration_counter % 5 == 0 or self.iteration_counter == 1:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        if self.rect.y > 800:
            self.get_damage()

        if self.is_attacking and self.standing:
            self.left = self.right = False
            now1 = pygame.time.get_ticks()
            if now1 - self.attack_timer >= 1000:
                self.is_attacking = False
            try:
                self.frames = self.cut_sheet(
                    load_image("data/hero/lukang/attack_5_2.png"),
                    5, 2, self.rect.x, self.rect.y
                )
            except Exception:
                print("отсутствует анимация атаки персонажа")
            for elem in enemies:
                elem.is_under_attack()

        # проверка перезарядки атаки
        # если прошло больше 3 секунд с последней атаки
        if pygame.sprite.spritecollideany(self, level.left_ones):
            for elem in level.left_ones:
                if pygame.sprite.spritecollideany(elem, main_character_group):
                    if abs(elem.rect.left == self.rect.right - 1) <= 2 and elem.rect.bottom - 1 <= self.rect.bottom + 45:
                        self.right = False
                        break
        if pygame.sprite.spritecollideany(self, level.right_ones):
            for elem in level.right_ones:
                if pygame.sprite.spritecollideany(elem, main_character_group):
                    if abs(elem.rect.right - 1 - self.rect.left) <= 2 and elem.rect.bottom - 1 <= self.rect.bottom + 45:
                        self.left = False
                        break
        if pygame.sprite.spritecollideany(self, level.surface_sprites) \
                and self.check_ground():
            self.rising_timer = 0
            self.moving = True  # если находится на земле, то может прыгать
            self.jumping = False  # self.moving - флаг нахождения на платформе
            self.rising = False
        else:
            self.moving = False
        if pygame.sprite.spritecollide(self, level.cup_sprites, True):
            inventory.add_item("coin")

        if not self.moving and not self.is_attacking:  # если не на земле
            try:
                self.frames = self.cut_sheet(
                    load_image("data/hero/lukang/jump_3_2.png"),
                    3, 2, self.rect.x, self.rect.y
                )
            except Exception:
                print("отсутствует анимация прыжка персонажа")
            if self.right:
                self.direction.x = 1
                self.rect = self.rect.move(2, 0)
            if self.left:
                try:
                    self.frames = self.cut_sheet(
                        load_image("data/hero/lukang/jump_3_2_left.png"),
                        3, 2, self.rect.x, self.rect.y
                    )
                except Exception:
                    print("отсутствует анимация прыжка персонажа")
                self.direction.x = -1
                self.rect = self.rect.move(-2, 0)
            if not self.rising:  # если не взлетает
                self.rect = self.rect.move(0, 1)  # падает
                self.moving = False  # анимация падения (или продолжение анимации прыжка)
            else:  # анимация взлета (ну или просто прыжка, если взлета нет)
                self.rect = self.rect.move(0, -5)  # взлетает до тех пор, пока self.rising_timer не ноль
                self.rising_timer -= 5  # rising_timer задается в функции jump
                if self.rising_timer == 0:
                    self.rising = False

        if self.moving and not self.is_attacking:
            if self.right == self.left:
                # изменение направления движения героя
                self.direction.x = 0

                if not self.jumping and not self.is_attacking:
                    try:
                        self.frames = self.cut_sheet(
                            load_image("data/hero/lukang/idle_5_1.png"),
                            5, 1, self.rect.x, self.rect.y
                        )
                    except Exception:
                        print("отсутствует анимация idle-анимации персонажа")
                    self.standing = True
            elif self.left:
                # изменение направления движения героя
                self.direction.x = -1

                try:
                    self.frames = self.cut_sheet(
                        load_image("data/hero/lukang/move_5_2_left.png"),
                        5, 2, self.rect.x, self.rect.y
                    )
                except Exception:
                    print("отсутствует анимация движения персонажа")
                self.rect = self.rect.move(-2, 0)  # анимация движения влево
                if not self.jumping:
                    self.standing = False
            elif self.right:
                # изменение направления движения героя
                self.direction.x = 1

                try:
                    self.frames = self.cut_sheet(
                        load_image("data/hero/lukang/move_5_2.png"),
                        5, 2, self.rect.x, self.rect.y)
                except Exception:
                    print("отсутствует анимация движения персонажа")
                self.rect = self.rect.move(2, 0)  # анимация движения вправо
                if not self.jumping:
                    self.standing = False
            else:
                # изменение направления движения героя
                self.direction.x = 0

    # определение направления движения
    def walking(self, direction):
        if direction == pygame.K_a:
            self.left = True
        elif direction == pygame.K_d:
            self.right = True

    # определение направления движения
    def stop_walking(self, direction):
        if direction == pygame.K_a:
            self.left = False
        elif direction == pygame.K_d:
            self.right = False

    # прыжок
    def jump(self):
        # переменная jumping позволяет передвигаться в воздухе
        # rising - взлет
        # rising_timer - таймер взлета, которое изменяется в update
        self.rising = True
        self.rising_timer += 300
        self.jumping = True
        self.moving = False
        self.standing = False
        self.rect = self.rect.move(0, -5)

    # получение урона от пуль и ходячих, если здоровье на нуле - игра окончена
    def get_damage(self):
        if not self.is_attacking:
            self.hp -= 1
            if self.hp == 0:
                game_over()

    # Атака в ближнем бою
    def attack(self):
        self.is_attacking = True
        if self.reloading and self.jumping:
            pass  # атака в прыжке (разработаю, когда будет анимация атаки в прыжке)
        elif self.reloading:  # гг производит атаку и перезаряжает ее
            # проверка для каждого игрока находится ли он в поле действия атаки
            self.reloading = True
            self.last = pygame.time.get_ticks()
            self.attack_timer = pygame.time.get_ticks()

    # Атака сюрикеном
    def shoot(self, target):
        if self.shuriken > 0 and not self.inventory_opened:
            self.shuriken -= 1
            Shuriken(self.rect.x, self.rect.y, target[0], target[1], shurikens)


    # Проверка на контакт с землёй
    def check_ground(self):
        for elem in level.surface_sprites:
            if pygame.sprite.spritecollideany(elem, main_character_group) \
                    and abs(elem.rect.top - self.rect.bottom) <= 2:
                return True
        return False


#  Класс всех врагов
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(enemies)
        self.hp = 5

    # получение урона от гг (функция attack)
    def is_under_attack(self):
        if pygame.sprite.spritecollideany(self, main_character_group):
            self.get_damage()

    # получение урона от гг (функция shoot)
    def is_getting_shot(self):
        if pygame.sprite.spritecollideany(self, shurikens):
            self.get_damage()

    # Получние урона
    def get_damage(self):
        self.hp -= 1
        if self.hp == 0:
            self.kill()
            enemies.remove(self)
            if self in archers:
                archers.remove(self)

    def update(self, shift):
        self.rect.x += shift


# Класс врагов дальнего боя
class Archer(Enemy):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = load_image("data/enemy/archer.png")
        except Exception:
            print("отсутствует анимация лучника")
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

    def update_sdvig_x(self, shift):
        self.rect.x += shift

    # выстрел, при инициализации класса передаются координаты стрелка
    def shoot(self):
        Bullet(
            self.rect.x, self.rect.y,
            main_character.rect.x, main_character.rect.y,
            bullets
        )


# Класс снаряда, выстреливаемого врагом дальнего боя
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, group):
        super().__init__(group)

        try:
            self.frames = self.cut_sheet(
                load_image("data/enemy/bottle_12_2.png"),
                12, 2, x, y
            )
        except Exception:
            print("отсутствует анимация бутылки")

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

        """сначала мы выясням, за сколько времени пуля пройдет гипотенузу
         и потом присваиваем скорости по x и y значения: расстояние по x или y
         время прохождения гипотенузы 4 - скорость прохождения гипотенузы"""

        if paths[1] <= 10:
            self.vy = 0
        else:
            self.vy = math.ceil(paths[1] / (hypot / 4))
        if paths[0] <= 20:
            self.vx = 0
        else:
            self.vx = math.ceil(paths[0] / (hypot / 4))

    # нарезка спрайт-сета на спрайты
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


# Класс снаряда, выпускаемого главным героем
class Shuriken(Bullet):
    def __init__(self, x, y, target_x, target_y, group):
        super().__init__(x, y, target_x, target_y, group)

        try:
            self.frames = self.cut_sheet(
                load_image("data/hero/lukang/shuriken_6_1.png"),
                6, 1, x, y
            )
        except Exception:
            print("отсутствует анимация сюрикена")

        self.rect = pygame.Rect(x, y, 32, 32)
        self.waiting = False
        self.touch_time = 0
        self.rect = pygame.Rect(x, y, 2 * 5, 2 * 5)

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.vx * self.dx, self.vy * self.dy)
        if pygame.sprite.spritecollideany(self, enemies):
            for elem in enemies:
                elem.is_getting_shot()  # поиск противника, в которого попали
            self.kill()
        if pygame.sprite.spritecollideany(self, level.surface_sprites):
            self.kill()


# Противник ближнего боя
class GroundEnemy(Enemy):
    def __init__(self, x, y, walking_range, shift):
        super().__init__()
        try:
            self.frames = self.cut_sheet(
                load_image("data/enemy/idle_1_1.png"),
                1, 1, x, y
            )
        except Exception:
            print("Отсутствует анимация бездействия гопника ближнего боя")
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

        self.shift = shift

    # нарезка спрайт-сетов на спрайты
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
        # сдвиг врага
        self.rect.x += args[0]

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

    def update_sdvig_x(self, shift):
        self.rect.x += shift

    """цикличное хождение влево-вправо от стартовой позиции
     до (стартовой позиции + walking_range)"""
    def walking(self):
        if self.rect.x + 1 > self.start_x + self.walking_range:

            try:
                self.frames = self.cut_sheet(
                    pygame.transform.flip(
                        load_image("data/enemy/move_3_1.png"), True, False
                    ),
                    3, 1, self.rect.x, self.rect.y
                )
            except Exception:
                print("отсутствует анимация передвижения гопника")

            self.direction = -1

        elif self.rect.x - 1 < self.start_x:
            try:
                self.frames = self.cut_sheet(
                    load_image("data/enemy/move_3_1.png"),
                    3, 1, self.rect.x, self.rect.y
                )
            except Exception:
                print("отсутствует анимация передвижения гопника")

            self.direction = 1
        self.rect = self.rect.move(1 * self.direction, 0)


if __name__ == '__main__':
    pygame.init()

    pygame.time.set_timer(SHOOTING_EVENT, 3000)

    pygame.display.set_caption('Приключение Лю Кэнга во Владимире')
    pygame.mouse.set_visible(False)

    # список уровней игры
    spisok_level = [level_0, level_1, level_2]

    run = True
    while run:
        menu.menu()
        for number in spisok_level:
            # принудительная инициализация гопника с бутылкой и Лю Кэнга
            ar = Archer(100, 250)
            enemies.add(ar)
            archers.append(ar)
            main_character = MainCharacter(2, 400)

            # создание уровня из класса и его запуск
            level = Level(number, screen, main_character)
            start_level()

            # принудительное удаление гопника с бутылкой
            ar.kill()
            archers.clear()

pygame.quit()
