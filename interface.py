import os
import sys

import pygame

from game_settings import screen, screen_width

pygame.init()


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


def draw_interface(hp):
    interface = pygame.sprite.Group()
    for i in range(hp):
        icon = pygame.sprite.Sprite(interface)
        try:
            icon.image = pygame.transform.scale(
                load_image("data/backpack.png"), (64, 64)
            )
        except Exception:
            print("не найдено изображение инвентаря")
        icon.rect = icon.image.get_rect()
        icon.rect.x = 10
        icon.rect.y = 10

        hearts = pygame.sprite.Sprite(interface)
        try:
            hearts.image = pygame.transform.scale(
                load_image('data/hurt_1_96_96.png'), (64, 64)
            )
        except Exception:
            print("не найдено изображение сердца")
        hearts.rect = hearts.image.get_rect()
        hearts.rect.x = screen_width - 96 - (85 * i)
    interface.draw(screen)


class Resource:
    def __init__(self, name, path, info):
        self.name = name
        self.amount = 0
        self.image = load_image(path)
        self.info = info


class Inventory:
    def __init__(self):
        try:
            self.recources = {
                "coin": Resource(
                    "Монетка", "data/coin_64_64.png",
                    "Золотая монетка. Используется для покупки предметов "
                    "и подсчёта очков"),
            }
        except Exception:
            print("не найдено изображений предметов инвентаря")

        self.inventory_panel = [None] * 8

    def get_amount(self, name):
        try:
            return self.recources[name].amount
        except KeyError:
            print("error")

    def add_item(self, name):
        try:
            self.recources[name].amount += 1
            print(self.recources[name].amount)
            self.update_inventory()
        except KeyError:
            print("error")

    def update_inventory(self):
        for name, resource in self.recources.items():
            if resource.amount != 0 and resource not in self.inventory_panel:
                # TODO: сделать оповещение в инфопанели об отсутствии места
                self.inventory_panel.insert(
                    self.inventory_panel.index(None), resource
                )
                self.inventory_panel.remove(None)

    def draw_inventory(self):
        x = y = 30
        side = 80
        step = 100

        pygame.draw.rect(screen, (182, 195, 206), (x - 20, y - 20, 430, 220))

        for cell in self.inventory_panel:
            pygame.draw.rect(screen, (200, 215, 227), (x, y, side, side))
            if cell is not None:
                font = pygame.font.SysFont("Times New Roman", 14)
                screen.blit(cell.image, (x + 10, y + 5))
                screen.blit(font.render(f"{cell.amount}", 1, "black"), (x + 65, y + 57))
            x += step

            if x == 430:
                x = 30
                y += step


inventory = Inventory()
