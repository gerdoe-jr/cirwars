import pygame

from client.core.client import Client


def init_pygame():
    pygame.init()
    pygame.font.init()


if __name__ == '__main__':
    init_pygame()

    Client().run()
