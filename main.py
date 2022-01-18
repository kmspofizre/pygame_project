import pygame

import game_settings

from menu import menu
from game_settings import screen
from level_characters import level, archers, main_character
from level_characters import shurikens, bullets, main_character_group, enemies
from cursor import cursor, cur
from sound import sound


def start_level():
    sound.play('game4', 10, 0.3)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sound.stop('game4')
            # pygame.quit()
            # sys.exit()
            if event.type == game_settings.SHOOTING_EVENT:
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

        main_character.update()
        # enemies.update(0)
        shurikens.update()
        bullets.update()
        bullets.draw(game_settings.screen)
        for archer in archers:
            archer.update()
        enemies.draw(screen)
        main_character_group.draw(game_settings.screen)
        game_settings.clock1.tick(game_settings.fps)
        # pygame.display.flip()
        # обработчик курсора
        if pygame.mouse.get_focused():
            cursor.draw(game_settings.screen)
        pygame.display.update()


if __name__ == '__main__':
    pygame.init()

    pygame.time.set_timer(game_settings.SHOOTING_EVENT, 3000)

    # инициализация звука и музыки

    pygame.display.set_caption('Приключение Лю Кэнга')
    # инициализация курсора
    pygame.mouse.set_visible(False)

    running = True
    while running:
        menu.menu()

        # main_character = MainCharacter()
        # we = GroundEnemy(150, 350, 40)
        # enemies_sp = [we, ar]  # список врагов

        start_level()
pygame.quit()
