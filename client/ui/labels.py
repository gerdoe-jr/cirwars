from client.ui.component import *
from shared.globals import TICK_SPEED

from client.ui.opengl import *


class Label(Component):
    def __init__(self, scene, x=0, y=0, w=0, h=0, text=''):
        super().__init__(scene.screen)

        self.scene = scene

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.text = text

        self.on_init()

    def render(self):
        w, h = FONT.render(self.text, True, (0, 0, 0)).get_size()

        # draw_rect((self.x + (self.w - w) // 2, self.y + h // 5, w, self.h - h // 5), (255, 255, 255))
        draw_clipped_text((self.x + self.w // 2, self.y, self.w, self.h), self.text, (0, 0, 0))
        # draw_text((self.x + (self.w - w) // 2, self.y + self.h - h // 1.5), (0, 0, 0), self.text)


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
        if event.type == pygame.MOUSEBUTTONUP:
            self.texting = self.x + self.w >= event.pos[0] >= self.x and \
                    self.y + self.h >= event.pos[1] >= self.y

        if event.type == pygame.KEYDOWN and self.texting:
            print('::keydown')
            if event.key != pygame.K_BACKSPACE:
                key = None
                try:
                    key = ord(chr(event.key).lower())
                except ValueError as e:
                    print(e)
                if key and chr(key) in self.allowed_symbols:
                    self.holding_key = key
            else:
                self.holding_key = pygame.K_BACKSPACE

        if event.type == pygame.KEYUP and self.holding_key == event.key and self.texting:
            self.holding_key = 0

        if self.holding_key and self.holding_key != pygame.K_BACKSPACE\
                and (not self.max_len or len(self.text) < self.max_len) and event.type == pygame.TEXTINPUT:
            self.text += chr(self.holding_key)

        if self.holding_key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

    def render(self):
        # def sub_render_text(text, color):
        #     font = self.font.render(text, True, color)
        #     w, h = font.get_size()
        #     real_w = w - 20 if w - 20 >= self.w else self.w
        #     real_x = -10 if w - 20 >= self.w else (self.w - w) // 2
        #     font_surf = pygame.Surface((real_w, self.h))
        #     font_surf.fill((255, 255, 255))
        #     font_surf.blit(font, (real_x, -h * 0.1))
        #     self.screen.blit(font_surf, (self.x - real_w // 2, self.y))

        if len(self.text):
            draw_clipped_text((self.x, self.y, self.w, self.h), self.text, (0, 0, 0) if not self.texting else (200, 200, 200))
        elif len(self.out_text):
            draw_clipped_text((self.x, self.y, self.w, self.h), self.out_text, (200, 200, 200))
        else:
            draw_rect((self.x + self.w // 2, self.y, self.w, self.h), (255, 255, 255) if not self.texting else (0, 0, 0))
            # pygame.draw.rect(self.screen, (255, 255, 255) if not self.texting else (0, 0, 0), (self.x + self.w // 2, self.y, self.w, self.h))

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
                self.y += 40 / TICK_SPEED
        else:
            if self.y > self.previous_y:
                self.y -= 40 / TICK_SPEED

        super().render()

    def action(self):
        pass
