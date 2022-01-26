from client.network import *
from client.renderer import *


class GameClient:
    def __init__(self):
        self.net_client = None

        self.run()

    def run(self):
        running = True

        pygame.init()
        pygame.font.init()

        size = 800, 600
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption('cirwars [v1]')

        scene_controller = SceneController(screen)
        scene_controller.current_scene = LoadingScene(scene_controller)
        scene_controller.next_scene = MainMenu(scene_controller)

        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    scene_controller.current_scene.on_event(event)

            if pygame.key.get_focused():
                scene_controller.current_scene.render()
                scene_controller.on_tick()

            pygame.display.flip()
            clock.tick(TICK_SPEED)


if __name__ == '__main__':
    client = GameClient()
