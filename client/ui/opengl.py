from OpenGL.GL import *

import pygame

import math
import sys


FONT = pygame.font.Font('./data/fonts/font.ttf', 72)
WIDTH = HEIGHT = 800


def init_opengl():
    glViewport(0, 0, WIDTH, HEIGHT)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def convert_x(x):
    return x / WIDTH * 2 - 1


def convert_y(y):
    return -(y / HEIGHT * 2 - 1)


def convert_w(w):
    return w / WIDTH * 2


def convert_h(h):
    return -h / HEIGHT * 2


def convert_pos(pos):
    x, y = pos

    return convert_x(x), convert_y(y)


def draw_surface(pos, surface):
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glWindowPos2d(pos[0], HEIGHT - pos[1] - surface.get_height())
    glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(surface.convert_alpha(), 'RGBA', True))


def draw_text(pos, color, text, size=None):
    if len(color) == 3:
        color = *color, 255
    surface = (FONT.render(text, True, color) if not size else pygame.font.Font('./data/fonts/font.ttf', size).render(text, True, color))

    draw_surface(pos, surface)


def draw_clipped_text(box, text, text_color, size=None, opacity=255):
    bx, by, bw, bh = box

    if len(text_color) == 3:
        text_color = *text_color, 255

    args = text, True, text_color, (255, 255, 255, 255)

    fsurface = FONT.render(*args) if not size else pygame.font.Font('./data/fonts/font.ttf', size).render(*args)
    w, h = fsurface.get_size()

    real_w = w - 20 if w - 20 >= bw else bw
    real_x = -10 if w - 20 >= bw else (bw - w) // 2

    font_surf = pygame.Surface((real_w, bh), pygame.SRCALPHA)
    font_surf.fill((255, 255, 255))

    font_surf.blit(fsurface, (real_x, -h * 0.1))

    font_surf.set_alpha(opacity)

    draw_surface((bx - real_w // 2, by), font_surf)


def draw_rect(rect, color):
    x, y, w, h = rect
    x, y, w, h = *convert_pos((x, y)), convert_w(w), convert_h(h)

    def eint(i):
        return int(i).to_bytes(8, sys.byteorder)

    # glPushMatrix()
    #
    # glColor4ub(*color)
    # glRectiv(eint(x), eint(y), eint(x + w), eint(y + h))
    #
    # glPopMatrix()

    glPushMatrix()
    glTranslatef(x, y, 0.0)

    if len(color) == 3:
        color = *color, 255
    else:
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glColor4ub(*color)
    glVertex2f(0, 0)
    glVertex2f(0, h)
    glVertex2f(w, h)
    glVertex2f(w, 0)
    glEnd()

    glPopMatrix()


def draw_circle(pos, r, color, num_segments=32):
    cx, cy = convert_pos(pos)
    r = convert_w(r)

    theta = 2 * math.pi / float(num_segments)
    c = math.cos(theta)
    s = math.sin(theta)

    x = r
    y = 0

    glPushMatrix()

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_TRIANGLE_FAN)

    if len(color) == 3:
        color = *color, 255

    for i in range(num_segments):
        glColor4ub(*color)
        glVertex2f(x + cx, y + cy)

        t = x
        x = c * x - s * y
        y = s * t + c * y

    glEnd()

    glPopMatrix()


