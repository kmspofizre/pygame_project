import pygame
import characters


pygame.init()
pygame.display.set_caption('Создание персонажей')
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
# инициализация игры
bullets = characters.bullets
shurikens = characters.shurikens
enemies = characters.enemies
main_character_gr = characters.main_character_gr
platforms = characters.platforms
clock1 = pygame.time.Clock()
FPS = 30
SHOOTING_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SHOOTING_EVENT, 3000)
main_character = characters.main_character
pl = characters.pl
ar = characters.ar
archers = [ar]  # список стрелков
we = characters.we
running = True
enemies_sp = [we, ar]  # список врагов

if __name__ == '__main__':
    screen.fill(pygame.Color('black'))
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SHOOTING_EVENT:  # выстрел
                for j in range(len(archers)):
                    archers[j].shoot()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    main_character.shoot(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and main_character.moving:
                    main_character.jump()
                if main_character.moving or main_character.jumping:
                    main_character.walking(event.key)
                if event.key == pygame.K_a:
                    main_character.attack()
            if event.type == pygame.KEYUP:
                main_character.stop_walking(event.key)
        main_character.update()
        enemies.update()
        shurikens.update()
        bullets.update()
        bullets.draw(screen)
        shurikens.draw(screen)
        main_character_gr.draw(screen)
        enemies.draw(screen)
        platforms.draw(screen)
        clock1.tick(FPS)
        pygame.display.flip()


