import sys
import pygame

from game_settings import screen, surface_color, screen_width, connection
from cursor import cursor, cur
from sound import sound


class Menu:
    def __init__(self, menu_item):
        self.menu_item = menu_item

    def render(self, screen, font, num_menu_item):
        font = pygame.font.Font('fonts/Asessorc.otf', 30)
        screen.blit(font.render('Copyright 2021-2022', 1, 'red'), (450, 700))

        font = pygame.font.Font('fonts/Acsiomasupershockc.otf', 50)
        for i in self.menu_item:
            if num_menu_item == i[5]:
                screen.blit(font.render(i[2], 1, i[4]), (i[0], i[1]))
            else:
                screen.blit(font.render(i[2], 1, i[3]), (i[0], i[1]))

    def menu(self):
        sound.play('game2', 10, 0.3)
        active_menu = True
        pygame.key.set_repeat(0, 0)
        font_menu = pygame.font.Font('fonts/Acsiomasupershockc.otf', 50)
        menu_item = 0
        while active_menu:
            screen.fill((0, 100, 200))
            mouse_coords = pygame.mouse.get_pos()

            for i in self.menu_item:
                if i[0] < mouse_coords[0] < i[0] + 155 \
                        and i[1] < mouse_coords[1] < i[1] + 50:
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
                if event.type == pygame.MOUSEMOTION:
                    cur.rect = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_item == 0:
                        sound.stop('game2')
                        active_menu = False
                    if menu_item == 1:
                        print('rules')
                    if menu_item == 2:
                        score()
                    if menu_item == 3:
                        sys.exit()

            if pygame.mouse.get_focused():
                cursor.draw(screen)

            pygame.display.update()


class EndMenu:
    def __init__(self, menu_items):
        self.menu_items = menu_items

    def render(self, screen, font, num_menu_item):
        font = pygame.font.SysFont("Times new Roman", 120)
        screen.blit(font.render("YOU DIED", 1, "red"), (312, 220))

        font = pygame.font.SysFont("Times New Roman", 30)

        for i in self.menu_items:
            if num_menu_item == i[5]:
                screen.blit(font.render(i[2], 1, i[4]), (i[0], i[1]))
            else:
                screen.blit(font.render(i[2], 1, i[3]), (i[0], i[1]))

    def menu(self):
        active_menu = True
        pygame.key.set_repeat(0, 0)
        font_menu = pygame.font.SysFont('Times New Roman', 50)
        menu_item = 0
        while active_menu:
            sound.stop("game4")
            screen.fill((0, 0, 0))
            mouse_coords = pygame.mouse.get_pos()

            if pygame.mouse.get_focused():
                cursor.draw(screen)

            for i in self.menu_items:
                if i[0] < mouse_coords[0] < i[0] + 150 \
                        and i[1] < mouse_coords[1] < i[1] + 50:
                    menu_item = i[5]

            self.render(screen, font_menu, menu_item)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if menu_item == 0:
                            active_menu = False
                            menu.menu()
                        if menu_item == 1:
                            sys.exit()
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                    if event.key == pygame.K_UP:
                        if menu_item > 0:
                            menu_item -= 1
                    if event.key == pygame.K_DOWN:
                        if menu_item < len(self.menu_items) - 1:
                            menu_item += 1
                if event.type == pygame.MOUSEMOTION:
                    cur.rect = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu_item == 0:
                        active_menu = False
                        menu.menu()
                    if menu_item == 1:
                        sys.exit()

            if pygame.mouse.get_focused():
                cursor.draw(screen)

            pygame.display.update()


def score():
    screen.fill(surface_color)

    font = pygame.font.Font('fonts/Asessorc.otf', 30)
    cur = connection.cursor()
    result = cur.execute("SELECT id, date, score FROM results").fetchall()
    result = sorted(result, key=lambda x: x[0], reverse=True)

    i = 0
    pygame.draw.line(
        screen, pygame.Color('white'), (64, 64 * i + 64),
        (screen_width - 64, 64 * i + 64), 5
    )

    columns_name = ['Date and time', 'Score']
    for i in range(2):
        name = columns_name[i]
        naimenovania = font.render(name, 1, pygame.Color('yellow'))
        naimenovania_rect = naimenovania.get_rect()
        naimenovania_rect.x = 500 * i + 128
        naimenovania_rect.y = 64 + 12
        screen.blit(naimenovania, naimenovania_rect)

    for i in range(9):
        pygame.draw.line(
            screen, pygame.Color('white'),
            (64, 64 * (i + 1) + 64),
            (screen_width - 64, 64 * (i + 1) + 64), 5
        )

        if i < 8:
            for k in range(2):
                text_rend = font.render(
                    str(result[i][k + 1]), 1, pygame.Color('yellow')
                )
                text_rect = text_rend.get_rect()
                text_rect.x = 500 * k + 128
                text_rect.y = (64 * (i + 1) + 76)
                screen.blit(text_rend, text_rect)

        for k in range(3):
            pygame.draw.line(screen, pygame.Color('white'),
                             (535 * k + 64, 64 * i + 64),
                             (535 * k + 64, 64 * (i + 1) + 64), 5
                             )

    active_menu = True
    while active_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active_menu = False
            if event.type == pygame.K_ESCAPE:
                active_menu = False

        pygame.display.flip()


# создание меню
menu_items = [(510, 210, u'Game', 'yellow', 'red', 0),
              (520, 280, u'Rules', 'yellow', 'green', 1),
              (530, 350, u'Best', 'yellow', 'brown', 2),
              (530, 420, u'Quit', 'yellow', 'black', 3)]
end_menu_items = [(515, 500, u'Back to Menu', 'white', 'red', 0),
                  (575, 550, u'Exit', 'white', 'red', 1)]
end_menu = EndMenu(end_menu_items)
menu = Menu(menu_items)
