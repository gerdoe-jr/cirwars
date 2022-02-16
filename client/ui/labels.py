from client.ui.component import *
from shared.globals import TICK_SPEED


class Label(Component):
    def __init__(self, scene, x=0, y=0, w=0, h=0, text=''):
        super().__init__(scene.screen)

        self.scene = scene

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.text = text
        self.font = pygame.font.Font('./data/fonts/font.ttf', 72)

        self.on_init()

    def render(self):
        font = self.font.render(self.text, True, (0, 0, 0))
        w, h = font.get_size()
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x + (self.w - w) // 2, self.y + h // 5, w, self.h - h // 5))
        self.screen.blit(font, (self.x + (self.w - w) // 2, self.y + self.h - h // 1.5))


class WritableLabel(Label):
    def __init__(self, scene, x=0, y=0, w=0, h=0, out_text='', allowed=None, max_len=0):
        super().__init__(scene, x, y, w, h)

        self.out_text = out_text

        if not allowed:
            self.allowed_symbols = list('qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()_-=+/`.,|:;"\' ')
        else:
            self.allowed_symbols = allowed

        self.texting = False
        self.holding_key = 0
        self.max_len = max_len

        self.on_init()

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.x + self.w >= event.pos[0] >= self.x and \
                    self.y + self.h >= event.pos[1] >= self.y:
                self.texting = True
            else:
                self.texting = False
        elif event.type == pygame.KEYDOWN:
            if event.key != pygame.K_BACKSPACE:
                key = 0
                try:
                    key = ord(char(event.key).lower())
                except ValueError:
                    pass
                if key and key in self.allowed_symbols:
                    self.holding_key = key
            else:
                self.holding_key = pygame.K_BACKSPACE
        elif event.type == pygame.KEYUP:
            self.holding_key = 0

        if self.holding_key:
            if self.holding_key != pygame.K_BACKSPACE and self.max_len and len(self.text) < self.max_len:
                self.text += self.holding_key
            elif self.holding_key == pygame.K_BACKSPACE and not len(self.text):
                self.text = self.text[:-1]

    def render(self):
        def sub_render_text(text, color):
            font = self.font.render(text, True, color)
            w, h = font.get_size()
            real_w = w - 30 if w - 30 >= self.w else self.w
            real_x = -15 if w - 30 >= self.w else (self.w - w) // 2
            font_surf = pygame.Surface((real_w, self.h))
            font_surf.fill((255, 255, 255))
            font_surf.blit(font, (real_x, -h * 0.1))
            self.screen.blit(font_surf, (self.x - real_w // 2, self.y))

        if len(self.text):
            sub_render_text(self.text, (0, 0, 0))
        elif len(self.out_text):
            sub_render_text(self.out_text, (200, 200, 200))
        else:
            pygame.draw.rect(self.screen, (255, 255, 255), (self.x + self.w // 2, self.y, self.w, self.h))

    def content(self):
        return self.text


class Button(Label):
    def on_init(self):
        self.hovered = False

        self.hovered_y = self.y + 10
        self.previous_y = self.y

    def on_event(self, event):
        def in_box(cursor):
            return self.x + self.w >= cursor[0] >= self.x and \
                self.y + self.h >= cursor[1] >= self.y

        if in_box(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
            self.action()
        else:
            self.hovered = in_box(pygame.mouse.get_pos())

    def render(self):
        if self.hovered:
            if self.y < self.hovered_y:
                self.y += 15 / TICK_SPEED
        else:
            if self.y > self.previous_y:
                self.y -= 15 / TICK_SPEED

        super().render()

    def action(self):
        pass
