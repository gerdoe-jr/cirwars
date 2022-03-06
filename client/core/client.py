import pygame
import cProfile

from client.core.interaction import InteractionClient
from client.core.network import NetworkClient
from client.core.game import GameClient
from shared.globals import TICK_SPEED

from client.ui.opengl import *


class Client:
    def __init__(self):
        self.interaction = InteractionClient()
        self.network = NetworkClient()
        self.game = GameClient(self.interaction, self.network)

    def run(self):
        running = True

        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.interaction.on_event(event)
                    self.game.on_event(event)

            self.network.on_tick()

            glClear(GL_COLOR_BUFFER_BIT)

            self.game.on_tick()  # cProfile.runctx('self.game.on_tick()', locals=locals(), globals=globals())
            self.interaction.on_tick()

            glFlush()
            pygame.display.flip()

            clock.tick(TICK_SPEED * 2)

        self.network.stop()
