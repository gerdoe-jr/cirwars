import pygame

from shared.globals import TICK_SPEED


class Component:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def render(self):
        pass

    def on_event(self, event):
        pass


class Label(Component):
    def __init__(self, scene, x=0, y=0, w=0, h=0, text=''):
        super().__init__(scene.screen)

        self.scene = scene

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.text = text
        self.font = pygame.font.Font('font.ttf', 72)

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.x + self.w >= event.pos[0] >= self.x and \
                    self.y + self.h >= event.pos[1] >= self.y:
                self.on_click()

    def on_click(self):
        self.action()

    def action(self):
        pass

    def render(self):
        font = self.font.render(self.text, True, (0, 0, 0))
        w, h = font.get_size()
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x + (self.w - w) // 2 - 5, self.y + h // 5, w + 5, self.h - h // 5))
        self.screen.blit(font, (self.x + (self.w - w) // 2, self.y + self.h - h // 1.5))


class WritableLabel(Label):
    def __init__(self, scene, x=0, y=0, w=0, h=0, out_text='', allowed_symbols=[]):
        super().__init__(scene, x, y, w, h)

        self.out_text = out_text
        self.allowed_symbols = allowed_symbols

        self.texting = False

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.x + self.w >= event.pos[0] >= self.x and \
                    self.y + self.h >= event.pos[1] >= self.y:
                self.on_click()
            else:
                self.texting = False

    def render(self):
        text = ''
        color = (0, 0, 0)
        if self.text:
            text = self.text
        elif self.out_text:
            color = (0, 0, 0, 128)
            text = self.out_text

        font = self.font.render(text, True, color)

        w, h = font.get_size()
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.x + (self.w - w) // 2 - 5, self.y + h // 5, w + 5, self.h - h // 5))
        self.screen.blit(font, (self.x, self.y))


class SceneController:
    DEFAULT_TIMEOUT = TICK_SPEED * 1

    def __init__(self, screen):
        self.screen = screen
        self.black_screen_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        self.current_scene = MainMenu(self)
        self.previous_scene = self.next_scene = None

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


class Scene(Component):
    def __init__(self, scene_controller):
        super().__init__(scene_controller.screen)

        self.scene_controller = scene_controller


class LoadingScene(Scene):
    def render(self):
        w, h = self.screen.get_size()
        self.screen.blit(pygame.font.Font('font.ttf', 24).render('(c) gerdoe', True, (255, 255, 255)), (w - 140, h - 40))


class MainMenu(Scene):
    class ConnectButton(Label):
        def action(self):
            print('lol?')
            self.scene.scene_controller.next_scene = ConnectMenu(self.scene.scene_controller)

    def __init__(self, scene_controller):
        super().__init__(scene_controller)

        w, h = self.screen.get_size()
        logo_size = (400, 100)
        button_size = (200, 50)

        bposx = w // 2 - button_size[0] // 2

        self.labels = [
            Label(self, w // 2 - logo_size[0] // 2, h // 4 - logo_size[1] // 2, *logo_size, text='cirwars'),
            self.ConnectButton(self, bposx, 6 * h // 10 - button_size[1] // 2, *button_size, text='connect'),
            Label(self, bposx, 7 * h // 10 - button_size[1] // 2, *button_size, text='settings'),
            Label(self, bposx, 8 * h // 10 - button_size[1] // 2, *button_size, text='exit')
        ]

    def on_event(self, event):
        for l in self.labels:
            l.on_event(event)

    def render(self):
        self.screen.fill((0, 0, 0))

        for l in self.labels:
            l.render()


class ConnectMenu(Scene):
    def __init__(self, scene_controller):
        super().__init__(scene_controller)

        w, h = self.screen.get_size()

        self.labels = [
            Label(self, w // 2 - 50, h // 2 - 50, 100, 100, text='lol?')
        ]

    def render(self):
        self.screen.fill((0, 0, 0))

        for l in self.labels:
            l.render()
