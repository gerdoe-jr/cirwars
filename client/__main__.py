import pygame

pygame.init()
pygame.font.init()

from client.core.client import Client


if __name__ == '__main__':
    Client().run()
