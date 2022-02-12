from client.ui import *


class LoadingScene(Scene):
    def render(self):
        w, h = self.screen.get_size()
        self.screen.blit(pygame.font.Font('./data/fonts/font.ttf', 24).render('(c) gerdoe', True, (255, 255, 255)), (w - 140, h - 40))


class MainMenu(Scene):
    class ConnectButton(Button):
        def action(self):
            print('lol?')
            self.scene.scene_controller.next_scene = ConnectMenu(self.scene.scene_controller)

    class SettingsButton(Button):
        pass

    class ExitButton(Button):
        def action(self):
            pygame.quit()

    def on_init(self):
        w, h = self.screen.get_size()
        logo_size = (400, 100)
        button_size = (200, 50)

        bposx = w // 2 - button_size[0] // 2

        self.components = [
            Label(self, w // 2 - logo_size[0] // 2, h // 4 - logo_size[1] // 2, *logo_size, text='cirwars'),
            self.ConnectButton(self, bposx, 6 * h // 10 - button_size[1] // 2, *button_size, text='connect'),
            self.SettingsButton(self, bposx, 7 * h // 10 - button_size[1] // 2, *button_size, text='settings'),
            self.ExitButton(self, bposx, 8 * h // 10 - button_size[1] // 2, *button_size, text='exit')
        ]

        self.bg_offset = 0

    def render(self):
        self.screen.fill((0, 0, 0))
        # background
        r = 20
        const = 30 + r
        w, h = self.screen.get_size()

        self.bg_offset += 10 / TICK_SPEED
        self.bg_offset %= r + const * 2

        for j in range(-1, h // int(2 * const + r) + 2):
            for i in range(-1, w // int(2 * const + r) + 2):
                x, y = i * (2 * const + r), j * (2 * const + r)

                x += self.bg_offset if j % 2 else -self.bg_offset

                c_x = 0
                if -r < x < w + r:
                    c_x = int((r + (x if j % 2 else w - x)) / (w + 2 * r) * 150)

                pygame.draw.circle(self.screen, (c_x, c_x, c_x), (x, y), r)

        for c in self.components:
            c.render()


class ConnectMenu(Scene):
    class OkButton(Button):
        def action(self):
            pass

    def on_init(self):
        w, h = self.screen.get_size()

        self.components = [
            WritableLabel(self, w // 2, h // 2 - 150, 100, 50, out_text='name'),
            WritableLabel(self, w // 2, h // 2 - 50, 100, 50, out_text='addr', allowed=list('0123456789.')),
            self.OkButton(self, w // 2 - 50, h // 2 + 50, 100, 50, text='ok')
        ]
