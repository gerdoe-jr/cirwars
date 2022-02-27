import pygame

from client.scenes import SceneController, MainMenu, LoadingScene


class InteractionClient:
    def __init__(self):
        screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption('cirwars')

        self.scene_controller = SceneController(screen)
        self.scene_controller.current_scene = LoadingScene(self.scene_controller)
        self.scene_controller.next_scene = MainMenu(self.scene_controller)

    def on_tick(self):
        if pygame.key.get_focused():
            self.scene_controller.render()

            pygame.display.flip()

        self.scene_controller.on_tick()

    def on_event(self, event):
        self.scene_controller.on_event(event)
