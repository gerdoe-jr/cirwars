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

    def on_tick(self):
        event = event_handler_instance.recv(EventReceiver.GAME)

        if event:
            event, info = event
            if event == ClientEvents.Game.START:
                self.started = True
                self.start()
            elif event == ClientEvents.Game.STOP:
                self.started = False

        if self.started:
            packets = self.network.received_packets.flush()

            for p in packets:
                if isinstance(p, ServerInfo):
                    print(p.__dict__)
                elif isinstance(p, PlayerSpawnInfo):
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

            player = self.context.world.get_character(self.client_id)

            if player and player.input:
                self.network.send_packet(player.to_net())
                print('sent')

            self.render()

    def render(self):
        if self.started:
            self.interaction.screen.fill((0, 0, 0))
            for pos, tile in self.context.collision.tiles.items():
                c = 255 // (tile + 1)
                color = (c, c, c)
                tile_size = self.context.collision.TILE_SIZE
                pos = (pos[0] * tile_size, pos[1] * tile_size)

                draw_rect((pos[0], pos[1], tile_size, tile_size), color)
                # pygame.draw.rect(self.interaction.screen, color, (pos[0], pos[1], tile_size, tile_size))

            for e in self.context.world.entities:
                color = (255, 255, 255) if e.client_id != self.client_id else (190, 255, 255)
                draw_circle((e.pos.x - 0.5 * Character.RADIUS, e.pos.y - 0.5 * Character.RADIUS), ClientCharacter.RADIUS, color)
                # pygame.draw.circle(self.interaction.screen, color, (e.pos.x, e.pos.y), ClientCharacter.RADIUS)

    def on_event(self, event):
        if self.started:
            char = self.context.world.get_character(self.client_id)
            if char:
                if event.type == pygame.KEYDOWN:
                    keys = 0
                    if event.key == pygame.K_RIGHT:
                        keys |= ClientCharacter.Input.RIGHT
                    if event.key == pygame.K_LEFT:
                        keys |= ClientCharacter.Input.LEFT
                    if event.key == pygame.K_UP:
                        keys |= ClientCharacter.Input.JUMP
                    if event.key == pygame.K_DOWN:
                        keys |= ClientCharacter.Input.SPEEDUP

                    print('{0:b}'.format(keys))

                    if char.input:
                        char.input.keys |= keys

                        print('char', '{0:b}'.format(char.input.keys))
                    else:
                        char.input = ClientCharacter.Input(char.pos.x, char.pos.y, keys)
