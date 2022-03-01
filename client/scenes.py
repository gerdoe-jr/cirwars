from client.ui import *
from shared.event_handler import ClientEvents, EventReceiver, event_handler_instance


class LoadingScene(Scene):
    def render(self):
        w, h = self.screen.get_size()
        draw_text((w - 140, h - 40), (255, 255, 255), '(c) gerdoe', 24)
        # self.screen.blit(pygame.font.Font('./data/fonts/font.ttf', 24).render('(c) gerdoe', True, (255, 255, 255)), (w - 140, h - 40))


class MainMenu(Scene):
    class ConnectButton(Button):
        def action(self):
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

    def render_before_components(self):
        self.screen.fill((0, 0, 0))

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

                draw_circle((x, y), r, (c_x, c_x, c_x))
                # pygame.draw.circle(self.screen, (c_x, c_x, c_x), (x, y), r)


class ConnectMenu(Scene):
    class OkButton(Button):
        trying_to_connect = False
        timeout = TICK_SPEED * 10
        count = 0
        connected = False

        def reset(self):
            self.trying_to_connect = False
            self.connected = False
            self.count = 0

        def action(self):
            server_address = (self.scene.components[1].content(), 0)
            nick = self.scene.components[0].content()
            nick = nick if len(nick) < 9 else nick[:8]
            event_handler_instance.send(EventReceiver.NETWORK, ClientEvents.Network.TRY_CONNECT, nick, server_address)
            self.trying_to_connect = True

        def on_tick(self):
            if self.connected:
                self.scene.scene_controller.next_scene = GameScene(self.scene.scene_controller)
                self.reset()
            elif self.trying_to_connect:
                event = event_handler_instance.recv(EventReceiver.INTERACTION)

                if event:
                    print('received interaction.net_connected')
                    self.reset()
                    self.connected = True
                    return

                self.count += 1

                if self.count >= self.timeout:
                    self.reset()
                    self.scene.scene_controller.next_scene = self.scene.scene_controller.previous_scene

    class NickLabel(WritableLabel):
        pass

    class AddressLabel(WritableLabel):
        pass

    def on_init(self):
        w, h = self.screen.get_size()

        self.components = [
            self.NickLabel(self, w // 2, h // 2 - 150, 100, 50, out_text='name'),
            self.AddressLabel(self, w // 2, h // 2 - 50, 100, 50, out_text='addr', allowed=list('0123456789.')),
            self.OkButton(self, w // 2 - 50, h // 2 + 50, 100, 50, text='ok')
        ]


class GameScene(Scene):
    def on_init(self):
        event_handler_instance.send(EventReceiver.GAME, ClientEvents.Game.START)

    def on_tick(self):
        event = event_handler_instance.recv(EventReceiver.INTERACTION)

        if event:
            if event[0] == ClientEvents.Interaction.NET_DISCONNECTED:
                event_handler_instance.send(EventReceiver.GAME, ClientEvents.Game.STOP)
                self.scene_controller.next_scene = self.scene_controller.previous_scene

    def render(self):
        p = 0
