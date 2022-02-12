import pygame


class Component:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def on_init(self):
        pass

    def render(self):
        pass

    def on_event(self, event):
        pass
