import os
import sys
import math

import pygame


bullets = pygame.sprite.Group()
shurikens = pygame.sprite.Group()
enemies = pygame.sprite.Group()
main_character_gr = pygame.sprite.Group()
platforms = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class MainCharacter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(main_character_gr)
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('blue'), (0, 0, 20, 20))
        self.items = dict()
        self.hp = 50
        self.rect = pygame.Rect(2, 350, 20, 20)
        self.moving = False
        self.rising = False
        self.jumping = False
        self.left = False
        self.right = False
        self.att = True
        self.last = 0
        self.rising_timer = 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, platforms):  # если находится на земле, то может прыгать
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
            self.rect = self.rect.move(-3, 0)
        elif self.right:
            self.rect = self.rect.move(3, 0)
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


class Platform(pygame.sprite.Sprite):

    # тестовое окружение

    def __init__(self):
        super().__init__(platforms)
        self.image = pygame.Surface((500, 100), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('grey'), (0, 0, 500, 100))
        self.rect = pygame.Rect(0, 400, 500, 200)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(enemies)
        self.hp = 5

    def is_under_attack(self):
        if pygame.sprite.spritecollideany(self, main_character_gr):  # получение урона от гг (функция attack)
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

        # проверка, стоит ли лучник на земле, если нет - падение

        if pygame.sprite.spritecollideany(self, platforms):
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
        if pygame.sprite.spritecollideany(self, main_character_gr):
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
    def __init__(self, x, y, walking_range):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('pink'), (0, 0, 20, 20))
        # начальная координата, которая является левой крайней точкой
        self.start_x = x
        self.rect = pygame.Rect(x, y, 20, 20)
        # конечная координата
        self.walking_range = walking_range
        self.moving = False
        self.attack = True
        self.cooldown = 3000
        self.last = 0
        self.direction = 1
        self.attack_clock = pygame.time.Clock()

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, platforms):

            # если стоит на земле, то запускается цикличный обход

            self.moving = True
            self.walking()
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)
        if pygame.sprite.spritecollideany(self, main_character_gr):
            if self.attack:
                main_character.get_damage()
                self.attack = False
                self.last = pygame.time.get_ticks()
            else:
                now = pygame.time.get_ticks()
                if now - self.last >= 3000:  # если с последней атаки прошло 3 и больше секунд
                    self.attack = True       # то можно атаковать снова
        if pygame.sprite.spritecollideany(self, shurikens):
            self.get_damage()

    def walking(self):
        # цикличное хождение влево-вправо от стартовой позиции до стартовая позиция + walking_range
        if self.rect.x + 1 > self.start_x + self.walking_range:
            self.direction = -1
        elif self.rect.x - 1 < self.start_x:
            self.direction = 1
        self.rect = self.rect.move(1 * self.direction, 0)


def game_over():
    global running
    running = False


main_character = MainCharacter()
pl = Platform()  # вместо нее должна быть поверхность игрового мира
ar = Archer(100, 250)
we = GroundEnemy(150, 350, 40)
enemies_sp = [we, ar]  # список врагов
archers = [ar]  # список стрелков
