import pygame
import random
import sys
import os

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


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


def terminate():
    pygame.quit()
    sys.exit()


intro_text = ["Здравствуйте"]


a = ['Clouds 1.png', 'Clouds 2.png', 'Clouds 4.png', 'Clouds 5.png', 'Clouds 6.png', 'Clouds 7.png', 'Clouds 8.png']
fon = pygame.transform.scale(load_image(random.choice(a)), (WIDTH, HEIGHT))
screen.blit(fon, (0, 0))

font = pygame.font.Font(None, 30)
text_coord = 50
for line in intro_text:
    string_rendered = font.render(line, 1, pygame.Color('black'))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN or \
                event.type == pygame.MOUSEBUTTONDOWN:
            terminate()

    pygame.display.flip()
    clock.tick(FPS)
