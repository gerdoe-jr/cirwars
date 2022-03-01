import random

from shared.world import *
from shared.protocol import *


class ServerCharacter(Character):
    def spawn(self, pos):
        self.alive = True
        self.pos = self.next_pos = Vector(pos[0] * Collision.TILE_SIZE * 1.5, pos[1] * Collision.TILE_SIZE * 1.5)

        self.world.on_character_spawn(self)

    def die(self):
        self.alive = False

        self.world.on_character_death(self)

    def to_net(self):
        return PlayerEntityInfo(self.client_id, self.pos.x, self.pos.y) if self.alive else None


class ServerWorld(GameWorld):
    planned_packets = []

    def on_player_input(self, client_id, packet):
        char = self.get_character(client_id)
        if char:
            char.on_input(packet)

    def on_player_connect(self, client_id):
        sp = self.context.collision.spawn_points
        ServerCharacter(self, client_id).spawn(sp[random.randrange(len(sp))])

    def on_player_disconnect(self, client_id):
        char = self.get_character(client_id)
        char.die()
        self.del_entity(char)

    def on_character_spawn(self, character):
        self.planned_packets += [PlayerSpawnInfo(character.client_id)]

    def on_character_death(self, character):
        self.planned_packets += [PlayerDeathInfo(character.client_id)]

    def to_net(self):
        result = self.planned_packets[:] + list(filter(lambda x: x, map(lambda x: x.to_net(), self.entities)))
        self.planned_packets.clear()

        return result
