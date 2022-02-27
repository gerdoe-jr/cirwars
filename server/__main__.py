from os import path, listdir
from pygame.time import Clock

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
        self.net_server = NetworkServer()
        self.context = None

    def tick(self):
        if self.context.world:
            self.context.world.tick()

        self.current_tick += 1

    def run(self):
        game_map = self.load_map()

        if not game_map:
            return

        game_map = list(map(lambda x: list(map(lambda y: int(y), list(x.rstrip('\n')))), game_map))

        for l in game_map:
            print(l)

        self.context = self.Context()

        self.context.world = GameWorld(self.context)
        self.context.collision = Collision(self.context, game_map)

        self.net_server.start()

        clock = Clock()

        while True:
            self.tick()

            clock.tick(TICK_SPEED)

    def load_map(self):
        for file in filter(lambda x: print(x) or path.isfile('./data/maps/' + x), listdir('./data/maps/')):
            file = './data/maps/' + file
            if file.lower().rstrip().endswith('.tmap'):
                o_file = open(file, 'r')
                data = o_file.readlines()
                o_file.close()
                return data
        return None


if __name__ == '__main__':
    server = GameServer()

    print('running server...')

    server.run()
