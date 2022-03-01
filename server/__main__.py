from pygame.time import Clock

from server.network import NetworkServer
from server.game_logic import ServerWorld, Collision
from shared.globals import *
from shared.protocol import *
from shared.context import *
from shared.misc import *


class GameServer:
    def __init__(self):
        self.current_tick = 0
        self.net_server = NetworkServer()
        self.context = None

        self.map_name = ''

    def on_packet(self, client_id, packet):
        if isinstance(packet, ClientInfo):
            pass
        elif isinstance(packet, ClientInputInfo):
            self.context.world.on_player_input(client_id, packet)

    def tick(self):
        for key in self.net_server.clients.keys():
            client = self.net_server.clients[key]

            if len(client.received_packets):
                with client.received_packets.lock:
                    packets = client.received_packets.packets[:]
                    client.received_packets.packets.clear()

                for packet in packets:
                    self.on_packet(key, packet)

        if self.context.world:
            self.context.world.tick()
            packets = self.context.world.to_net()

            if packets:
                for c in self.net_server.clients.values():
                    c.send_packets(packets)

        self.current_tick += 1

    def run(self):
        self.map_name, game_map = load_map()

        if not game_map:
            return

        game_map = list(map(lambda x: list(map(lambda y: int(y), list(x.rstrip('\n')))), game_map))

        for l in game_map:
            print(l)

        self.context = Context()
        self.net_server.context = self.context

        self.context.world = ServerWorld(self.context)
        self.context.collision = Collision(self.context, game_map)

        self.net_server.map_name = self.map_name

        self.net_server.start()

        clock = Clock()

        while True:
            self.tick()

            clock.tick(TICK_SPEED)


if __name__ == '__main__':
    server = GameServer()

    print('running server...')

    server.run()
