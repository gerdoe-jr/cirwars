from client.ui.component import *
from shared.globals import TICK_SPEED


class SceneController:
    DEFAULT_TIMEOUT = TICK_SPEED * 0.5

    def __init__(self, screen):
        self.screen = screen
        self.black_screen_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        self.current_scene = self.previous_scene = self.next_scene = None

        self.next_scene_timeout = self.DEFAULT_TIMEOUT

    def on_tick(self):
        if self.current_scene:
            self.current_scene.render()

        if self.next_scene and self.next_scene_timeout == 0:
            print('next_scene')
            self.previous_scene = self.current_scene
            self.current_scene = self.next_scene
            self.next_scene = None

            self.next_scene_timeout -= 1

        if self.next_scene and self.next_scene_timeout < -self.DEFAULT_TIMEOUT:
            self.next_scene_timeout = self.DEFAULT_TIMEOUT

        if self.next_scene_timeout >= -self.DEFAULT_TIMEOUT:
            pygame.draw.rect(self.black_screen_surface,
                             (0, 0, 0, 255 - int(abs(self.next_scene_timeout / self.DEFAULT_TIMEOUT) * 255)),
                             (0, 0, self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(self.black_screen_surface, (0, 0, self.screen.get_width(), self.screen.get_height()))
            self.next_scene_timeout -= 1

    def on_event(self, event):
        self.current_scene.on_event(event)


class Scene(Component):
    def __init__(self, scene_controller):
        super().__init__(scene_controller.screen)

        self.scene_controller = scene_controller
        self.components = []

        self.on_init()

    def on_event(self, event):
        for c in self.components:
            c.on_event(event)

    def render(self):
        self.screen.fill((0, 0, 0))

        self.render_before_components()
        self.render_components()
        self.render_after_components()

    def render_before_components(self):
        pass

    def render_components(self):
        for c in self.components:
            c.render()

    def render_after_components(self):
        pass
