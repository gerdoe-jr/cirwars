import pygame

from client.core.interaction import InteractionClient
from client.core.network import NetworkClient
from shared.globals import TICK_SPEED


class Client:
    def __init__(self):
        self.interaction = InteractionClient()
        self.network = NetworkClient()

    def run(self):
        running = True

        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.interaction.on_event(event)

            self.interaction.on_tick()
            self.network.on_tick()

            clock.tick(TICK_SPEED * 2)

        self.network.stop()
