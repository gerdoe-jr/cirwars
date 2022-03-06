import pygame

from client.scenes import SceneController, MainMenu, LoadingScene
from client.ui.opengl import *


class InteractionClient:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)

        init_opengl()

        pygame.display.set_caption('cirwars')

        self.scene_controller = SceneController(self.screen)
        self.scene_controller.current_scene = LoadingScene(self.scene_controller)
        self.scene_controller.next_scene = MainMenu(self.scene_controller)

    def on_tick(self):
        self.scene_controller.render()
        self.scene_controller.on_tick()

    def on_event(self, event):
        self.scene_controller.on_event(event)
