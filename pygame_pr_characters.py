import os
import sys
import math

import pygame


pygame.init()
pygame.display.set_caption('Создание персонажей')
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
# выстрел каждые 3 секунды
SHOOTING_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOOTING_EVENT, 3000)


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
        self.hp = 3
        self.rect = pygame.Rect(2, 350, 20, 20)
        self.moving = False
        self.jumping = False
        self.left = False
        self.right = False

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, platforms):
            self.moving = True
            self.jumping = False
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)
            self.moving = False
        if self.left and self.right:
            pass
        elif self.left:
            self.rect = self.rect.move(-3, 0)
        elif self.right:
            self.rect = self.rect.move(3, 0)

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
        self.jumping = True
        self.rect = self.rect.move(0, -100)


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(platforms)
        self.image = pygame.Surface((500, 100), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('grey'), (0, 0, 500, 100))
        self.rect = pygame.Rect(0, 400, 500, 200)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(enemies)


class Archer(Enemy):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, pygame.Color('green'), (0, 0, 20, 20))
        self.rect = pygame.Rect(x, y, 20, 20)
        self.moving = False

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, platforms):
            self.moving = True
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)

    def shoot(self):
        Bullet(self.rect.x, self.rect.y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullets)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"),
                           (5, 5), 5)
        self.rect = pygame.Rect(x, y, 2 * 5, 2 * 5)
        # получение координат главного героя
        self.target_x = main_character.rect.x
        self.target_y = main_character.rect.y
        targets = [self.target_x, self.target_y]
        # нахождение расстояния между стрелком и главным героем
        paths = [abs(self.target_x - x), abs(self.target_y - y)]
        coords = [x, y]
        hypot = math.hypot(paths[0], paths[1])
        for_direction = [1, 1]
        # определение направления полета снаряда
        self.dx, self.dy = map(lambda i:  for_direction[i] * 1 if coords[i] - targets[i] < 0 else -1, range(2))
        # сначала мы выясням, за сколько времени пуля пройдет гипотенузу
        # и потом присваиваем скорости по x и y значения: расстояние по x или y / время прохождения гипотенузы
        # 4 - скорость прохождения гипотенузы (выбрал сам)
        self.vx = math.ceil(paths[0] / (hypot / 4))
        self.vy = math.ceil(paths[1] / (hypot / 4))

    def update(self):
        self.rect = self.rect.move(self.vx * self.dx, self.vy * self.dy)


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
        self.direction = 1

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, platforms):
            self.moving = True
            self.walking()
        else:
            self.moving = False
        if not self.moving:
            self.rect = self.rect.move(0, 1)

    def walking(self):
        # цикличное хождение влево-вправо от
        if self.rect.x + 1 > self.start_x + self.walking_range:
            self.direction = -1
        elif self.rect.x - 1 < self.start_x:
            self.direction = 1
        self.rect = self.rect.move(1 * self.direction, 0)


if __name__ == '__main__':
    running = True
    fps = 30
    clock1 = pygame.time.Clock()
    screen.fill(pygame.Color('black'))

    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    main_character_gr = pygame.sprite.Group()
    main_character = MainCharacter()
    platforms = pygame.sprite.Group()
    pl = Platform()
    ar = Archer(100, 250)
    ar1 = Archer(300, 380)
    we = GroundEnemy(150, 350, 40)
    archers = ar, ar1

    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
        main_character.update()
        enemies.update()
        bullets.update()
        bullets.draw(screen)
        main_character_gr.draw(screen)
        enemies.draw(screen)
        platforms.draw(screen)
        clock1.tick(fps)
        pygame.display.flip()
