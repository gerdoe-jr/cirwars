import pygame

from client.scenes import SceneController, MainMenu, LoadingScene
from client.ui.opengl import *


class InteractionClient:
    def __init__(self):
        w, h = 800, 800

        self.screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.OPENGL)

        init_opengl(w, h)

        pygame.display.set_caption('cirwars')

        self.scene_controller = SceneController(self.screen)
        self.scene_controller.current_scene = LoadingScene(self.scene_controller)
        self.scene_controller.next_scene = MainMenu(self.scene_controller)

    def on_tick(self, *additional_render):
        glClear(GL_COLOR_BUFFER_BIT)
        for r in additional_render:
            r()
        self.scene_controller.render()
        glFlush()
        pygame.display.flip()

        self.scene_controller.on_tick()

    def on_event(self, event):
        self.scene_controller.on_event(event)
