import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        else:
            raise ValueError("Vector doesn't support {} addition".format(type(other)))

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        else:
            raise ValueError("Vector doesn't support {} subtraction".format(type(other)))

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.length() * other.length() * math.cos(self.angle(other))
        elif isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        else:
            raise ValueError("Vector doesn't support {} multiplication".format(type(other)))

    def __div__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x / other, self.y / other)
        else:
            raise ValueError("Vector doesn't support {} division".format(type(other)))


def distance(first, second):
    return length(first - second)


def dot(vec):
    return vec.x ** 2 + vec.y ** 2


def center(first, second):
    if isinstance(second, Vector):
        return Vector((first.x + second.x) / 2, (first.y + second.y) / 2)
    else:
        raise ValueError("Vector doesn't support {} centering".format(type(second)))


def normalize(vec):
    return vec / length(vec)


def angle(first, second):
    if isinstance(second, Vector):
        return math.acos((first.x * second.x + first.y * second.y) / math.sqrt(dot(first) * dot(second)))
    else:
        raise ValueError("Vector doesn't support {} multiplication".format(type(second)))


def length(vec):
    return math.sqrt(dot(vec))


def mix(first, second, interpolate):
    return (1 - interpolate) * first + second * interpolate
