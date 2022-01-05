import os
import sys
import math
from pygame_pr_characters import MainCharacter, Platform, Enemy, Archer, Bullet, GroundEnemy

import pygame


pygame.init()
pygame.display.set_caption('Создание персонажей')
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
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




class Resource(MainCharacter):
    def __init__(self, name, path, info):
        super().__init__()
        self.name = name
        self.amount = 0
        self.image = load_image(path)
        self.info = info


class Inventory:
    def __init__(self):
        super(Inventory, self).__init__()
        icon = pygame.sprite.Sprite(interface)
        icon.image = pygame.transform.scale(load_image("backpack.png"), (64, 64))
        icon.rect = icon.image.get_rect()
        icon.rect.x = 10
        icon.rect.y = 10
        self.recources = {
            "coin": Resource("Монетка", "coin_front.jpg", "Золотая монетка. Используется для покупки предметов "
                                                                "и подсчёта очков"),
            "mushroom": Resource("Красный гриб", "mushroom.png", "Красный гриб. Используется для временного "
                                                                       "усиления"),
        }

        self.inventory_panel = [None] * 8

    def get_amount(self, name):
        try:
            return self.recources[name].amount
        except KeyError:
            print("error")

    def add_item(self, name):
        try:
            self.recources[name].amount += 1
            self.update_inventory()
        except KeyError:
            print("error")

    def update_inventory(self):
        for name, resource in self.recources.items():
            if resource.amount != 0 and resource not in self.inventory_panel:
                # TODO: сделать оповещение в инфопанели об отсутствии места
                self.inventory_panel.insert(self.inventory_panel.index(None), resource)
                self.inventory_panel.remove(None)

    def draw_inventory(self):
        x = y = 30
        side = 80
        step = 100

        pygame.draw.rect(screen, (182, 195, 206), (x - 20, y - 20, 430, 220))

        for cell in self.inventory_panel:
            pygame.draw.rect(screen, (200, 215, 227), (x, y, side, side))
            if cell is not None:
                screen.blit(cell.image, (x + 15, x + 5))
            x += step

            if x == 430:
                x = 30
                y += step


if __name__ == '__main__':
    running = True
    fps = 30
    clock1 = pygame.time.Clock()
    screen.fill(pygame.Color('black'))

    interface = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    main_character_gr = pygame.sprite.Group()
    main_character = MainCharacter()
    platforms = pygame.sprite.Group()
    pl = Platform()
    ar = Archer(100, 250)
    ar1 = Archer(300, 380)
    we = GroundEnemy(150, 350, 40)
    inventory = Inventory()
    archers = ar, ar1
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
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
            if keys[pygame.K_TAB]:
                inventory.draw_inventory()
        main_character.update()
        enemies.update()
        bullets.update()
        bullets.draw(screen)
        main_character_gr.draw(screen)
        enemies.draw(screen)
        platforms.draw(screen)
        interface.draw(screen)
        clock1.tick(fps)
        pygame.display.flip()
