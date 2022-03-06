import pygame

pygame.init()
pygame.font.init()

from client.core.client import Client
from client.ui.opengl import *
from shared.misc import *
import random


if __name__ == '__main__':
    Client().run()

    # clock = pygame.time.Clock()
    #
    # w, h = 800, 800
    #
    # screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
    #
    # init_opengl(w, h)
    #
    # pygame.display.set_caption('cirwars')
    #
    # name, g_map = load_map()
    #
    # g_map = list(map(lambda x: list(map(lambda y: int(y), list(x.rstrip('\n')))), g_map))
    #
    # for l in g_map:
    #     print(l)
    #
    # player_pos = 0, 0
    # holds = False
    # key = None
    #
    # while True:
    #     glClear(GL_COLOR_BUFFER_BIT)
    #     for y in range(len(g_map)):
    #         for x in range(len(g_map[y])):
    #             rect = (w / 2 + x * 32 - player_pos[0], h / 2 + y * 32 - player_pos[1], 32, 32)
    #             draw_rect(rect, (random.randrange(255) * g_map[y][x], random.randrange(255) * g_map[y][x], random.randrange(255) * g_map[y][x]))
    #
    #     draw_circle((w / 2, h / 2), 16, (200, 255, 255))
    #
    #     glFlush()
    #     pygame.display.flip()
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #         elif event.type == pygame.KEYDOWN:
    #             holds = True
    #             key = event.key
    #         elif event.type == pygame.KEYUP:
    #             holds = False
    #             key = None
    #
    #     if holds:
    #         if key == pygame.K_RIGHT:
    #             player_pos = player_pos[0] + 8, player_pos[1]
    #         if key == pygame.K_LEFT:
    #             player_pos = player_pos[0] - 8, player_pos[1]
    #         if key == pygame.K_UP:
    #             player_pos = player_pos[0], player_pos[1] - 8
    #         if key == pygame.K_DOWN:
    #             player_pos = player_pos[0], player_pos[1] + 8
    #
    #     clock.tick(120)
