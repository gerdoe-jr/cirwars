from shared.vecmath import *


class Collision:
    TILE_SIZE = 64

    def __init__(self, context, game_map):
        self.context = context
        self.tiles = {}

        for i in range(len(game_map)):
            for j in range(len(game_map[i])):
                if game_map[i][j] > 0:
                    self.tiles[(j, i)] = game_map[i][j]

    def get_tile(self, x, y):
        index = (x // self.TILE_SIZE, y // self.TILE_SIZE)

        return self.tiles[index] if index in self.tiles.keys() else None

    def move_box(self, pos, vel, box_size, elasticity=0):
        dist = length(vel)
        max_d = int(dist) + 1

        if dist > 0.00001:
            fraction = 1 / max_d

            for i in range(max_d):
                new_pos = pos + vel * fraction

                if self.test_box(new_pos, box_size):
                    hits = 0

                    if self.test_box(Vector(pos.x, new_pos.y), box_size):
                        new_pos.y = pos.y
                        vel.y *= -elasticity
                        hits += 1

                    if self.test_box(Vector(new_pos.x, pos.y), box_size):
                        new_pos.x = pos.x
                        vel.x *= -elasticity
                        hits += 1

                    if not hits:
                        new_pos = pos
                        vel *= -elasticity

                pos = new_pos

        return pos, vel

    def test_box(self, pos, box_size):
        box_size *= 0.5
        return self.get_tile(pos.x - box_size.x, pos.y - box_size.y) or\
            self.get_tile(pos.x + box_size.x, pos.y - box_size.y) or\
            self.get_tile(pos.x - box_size.x, pos.y + box_size.y) or\
            self.get_tile(pos.x + box_size.x, pos.y + box_size.y)


class GameWorld:
    GRAVITY = Vector(0, 0.30)

    def __init__(self, context):
        self.context = context

        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def del_entity(self, entity):
        self.entities.remove(entity)

    def find_entities(self, pos: Vector, radius: float, entity_type=None):
        output = []
        for entity in self.entities:
            if entity.pos.distance(pos) <= radius:
                if entity_type is None:
                    output.append(entity)
                elif isinstance(entity, entity_type):
                    output.append(entity)

        return output

    def move_character(self, char):
        new_pos, char.velocity = self.context.collision \
            .move_box(char.pos, char.velocity, Vector(Character.RADIUS, Character.RADIUS))

        dist = distance(char.pos, new_pos)
        max_d = int(dist) + 1
        last_pos = char.pos

        near_characters = self.find_entities(center(char.pos, new_pos), dist * 0.8, Character)

        for i in range(max_d):
            inter = i / dist
            temp_pos = mix(char.pos, new_pos, inter)

            for o_char in near_characters:
                char_dist = distance(temp_pos, o_char.pos)

                if Character.RADIUS > char_dist >= 0:
                    if inter > 0:
                        return last_pos
                    elif distance(temp_pos, o_char.pos) > char_dist:
                        return new_pos

            last_pos = temp_pos

        return new_pos

    def tick(self):
        for entity in self.entities:
            entity.tick()

        for entity in self.entities:
            entity.pos = entity.next_pos
            if isinstance(entity, Character):
                entity.velocity += self.GRAVITY

        for entity in self.entities:
            entity.post_tick()


class GameEntity:
    def __init__(self, world: GameWorld):
        self.world = world
        self.pos = Vector(0, 0)
        self.next_pos = Vector(0, 0)

        self.world.add_entity(self)

    def __del__(self):
        self.world.del_entity(self)

    def tick(self):
        pass

    def post_tick(self):
        pass

    def to_net(self):
        pass


class Character(GameEntity):
    RADIUS = 36

    class Input:
        LEFT = 1
        RIGHT = 2
        JUMP = 4
        SPEEDUP = 8

        def __init__(self, x, y, keys):
            self.cursor = Vector(x, y)
            self.keys = keys

        def is_left(self):
            return self.keys & self.LEFT

        def is_right(self):
            return self.keys & self.RIGHT

        def is_jump(self):
            return self.keys & self.JUMP

        def is_speedup(self):
            return self.keys & self.SPEEDUP

    def __init__(self, world: GameWorld):
        super().__init__(world)
        self.velocity = Vector(0, 0)
        self.input = None

        self.speedup_timeout = 0

    def tick(self):
        if self.input:
            if self.input.is_left():
                self.velocity.x -= 1
            if self.input.is_right():
                self.velocity.x += 1
            if self.is_grounded() and self.input.is_jump():
                self.velocity.y -= 1
            if not self.speedup_timeout and self.input.is_speedup():
                self.velocity *= 1.5

        self.next_pos = self.world.move_character(self)

        if self.speedup_timeout:
            self.speedup_timeout -= 1

    def to_net(self):
        pass

    def is_grounded(self):
        dt = self.pos
        dt.y += self.RADIUS
