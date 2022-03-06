import pygame

from client.ui.opengl import *

from shared.event_handler import ClientEvents, EventReceiver, event_handler_instance
from shared.protocol import *
from shared.world import *
from shared.context import *
from shared.misc import *


class ClientWorld(GameWorld):
    pass


class ClientCharacter(Character):
    def to_net(self):
        if self.input:
            packet = ClientInputInfo(self.pos.x, self.pos.y, self.input.keys)
            self.input = None

            return packet
        return None


class GameClient:
    def __init__(self, interaction, network):
        self.interaction = interaction
        self.network = network

        self.started = False
        self.context = None

        self.client_id = 0
        self.pos = Vector(0, 0)

    def start(self):
        self.client_id = self.network.client_id
        map_name, game_map = load_map(self.network.map_name)

        if not game_map:
            self.started = False
            pygame.quit()

        game_map = list(map(lambda x: list(map(lambda y: int(y), list(x.rstrip('\n')))), game_map))

        for l in game_map:
            print(l)

        self.context = Context()

        self.context.world = ClientWorld(self.context)
        self.context.collision = Collision(self.context, game_map)

    def on_packets(self, packets):
        for p in packets:
            if isinstance(p, PlayerSpawnInfo):
                char = self.context.world.get_character(p.client_id)
                if not char:
                    char = ClientCharacter(self.context.world, p.client_id)

                char.alive = True

            elif isinstance(p, PlayerEntityInfo):
                char = self.context.world.get_character(p.client_id)
                if not char:
                    ClientCharacter(self.context.world, p.client_id)
                else:
                    char.pos = Vector(p.x, p.y)

            elif isinstance(p, PlayerDeathInfo):
                char = self.context.world.get_character(p.client_id)
                if not char:
                    char = ClientCharacter(self.context.world, p.client_id)

                char.alive = False

            elif isinstance(p, ServerInfo):
                self.network.map_name = p.map_name.decode('utf-8').rstrip('\x00')
                self.client_id = p.client_id

    def on_tick(self):
        event = event_handler_instance.recv(EventReceiver.GAME)

        if event:
            kind, info = event
            if kind == ClientEvents.Game.START:
                self.started = True
                self.start()
            elif kind == ClientEvents.Game.STOP:
                self.started = False
                self.network.stop()

        if self.started:
            if event:
                kind, info = event
                if kind == ClientEvents.Game.NET_RECEIVED:
                    self.on_packets(*info)

            keys = pygame.key.get_pressed()
            if keys:
                self.on_pressed_keys(keys)

            player = self.context.world.get_character(self.client_id)

            if player and player.input:
                self.network.send_packet(player.to_net())

            self.render()

    def render(self):
        if self.started:
            w, h = WIDTH, HEIGHT
            for y in range(len(self.context.collision.tiles)):
                for x in range(len(self.context.collision.tiles[y])):
                    if abs(x - self.pos.x // Collision.TILE_SIZE) > 7 or\
                            abs(y - self.pos.y // Collision.TILE_SIZE) > 7 or\
                            not self.context.collision.tiles[y][x]:
                        continue

                    pos = w / 2 + x * Collision.TILE_SIZE - self.pos.x, h / 2 + y * Collision.TILE_SIZE - self.pos.y

                    c = 255 // self.context.collision.tiles[y][x]
                    color = (c, c, c)

                    draw_rect((*pos, Collision.TILE_SIZE, Collision.TILE_SIZE), color)

            for e in self.context.world.entities:
                if not e.alive:
                    continue
                x, y = e.pos.x, e.pos.y
                color = (255, 255, 255)

                if e.client_id == self.client_id:
                    self.pos = Vector(e.pos.x, e.pos.y)
                    x, y = WIDTH / 2, HEIGHT / 2
                    color = (190, 255, 255)
                else:
                    x, y = w / 2 + x - self.pos.x, h / 2 + y - self.pos.y

                if abs(x - self.pos.x // Collision.TILE_SIZE) > 7 or \
                        abs(y - self.pos.y // Collision.TILE_SIZE) > 7:
                    draw_circle((x, y), Character.RADIUS, color)

    def on_pressed_keys(self, keys):
        char = self.context.world.get_character(self.client_id)
        if char:
            i_keys = 0
            if keys[pygame.K_RIGHT]:
                i_keys |= ClientCharacter.Input.RIGHT
            if keys[pygame.K_LEFT]:
                i_keys |= ClientCharacter.Input.LEFT
            if keys[pygame.K_UP]:
                i_keys |= ClientCharacter.Input.JUMP
            if keys[pygame.K_DOWN]:
                i_keys |= ClientCharacter.Input.SPEEDUP

            if not i_keys:
                return

            if char.input:
                char.input.keys |= i_keys
            else:
                char.input = ClientCharacter.Input(char.pos.x, char.pos.y, i_keys)

    def on_event(self, event):
        if self.started:
            pass

