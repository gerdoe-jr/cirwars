from os import path, listdir
from pygame import time

from server.network import NetworkServer
from server.game_logic import GameWorld, Collision
from shared.globals import *


class GameServer:
    class Context:
        def __init__(self):
            self.world = None
            self.collision = None

    def __init__(self):
        self.current_tick = 0
        self.net_server = None
        self.context = None

        self.run()

    def tick(self):
        pass

    def run(self):
        game_map = self.load_map()

        if not game_map:
            return

        game_map = list(map(lambda x: list(map(lambda y: int(y), list(x.rstrip('\n')))), game_map))

        for l in game_map:
            print(l)

        self.net_server = NetworkServer()
        self.context = self.Context()

        self.context.world = GameWorld(self.context)
        self.context.collision = Collision(self.context, game_map)

        clock = time.Clock()

        while True:
            self.tick()
            clock.tick(TICK_SPEED)

    def load_map(self):
        for file in filter(lambda x: path.isfile(x), listdir()):
            if file.lower().endswith('.tmap'):
                o_file = open(file, 'r')
                data = o_file.readlines()
                o_file.close()
                return data
        return None


if __name__ == '__main__':
    server = GameServer()

    print('running server...')

    server.run()
