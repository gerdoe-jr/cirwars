import struct


# only trusted strings go here
def class_by_name(name):
    return eval(name)


class BasePacket:
    def format(self):
        pass

    def packet_type(self):
        PACKET_TYPES.index(type(self).__name__)

    def serialize(self):
        pass

    def inner_deserialize(self, info):
        pass

    @staticmethod
    def deserialize(bin_info):
        (packet_type,) = struct.unpack("!q", bin_info[0:5])

        packet = class_by_name(PACKET_TYPES[packet_type])()

        others = struct.unpack("!" + packet.format(), bin_info[5:])
        return packet.inner_deserialize(others)


# server packets
class PlayerEntityInfo(BasePacket):
    def __init__(self):
        self.x = 0
        self.y = 0

    def serialize(self):
        return struct.pack("!3q",
                           self.packet_type(),
                           self.x,
                           self.y)

    def inner_deserialize(self, info):
        (
            self.x,
            self.y,
        ) = info


# client packets
class PlayerInputInfo(BasePacket):
    def __init__(self):
        self.cur_x = 0
        self.cur_y = 0

        self.keys = 0

    def serialize(self):
        return struct.pack("!4q",
                           self.packet_type(),
                           self.cur_x,
                           self.cur_y,
                           self.keys)

    def inner_deserialize(self, info):
        (
            self.cur_x,
            self.cur_y,
            self.keys
        ) = info


PACKET_TYPES = list(
    map(lambda p: p.__name__,
        [
            PlayerEntityInfo,

            PlayerInputInfo,
        ])
)
