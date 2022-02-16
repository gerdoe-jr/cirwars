import struct
from threading import Lock


class BasePacket:
    def __init__(self, *attrs):
        str_format = ''

        for attr in attrs:
            self.__setattr__(attr[0], attr[2])
            str_format += attr[1]

        if not getattr(self, "str_format", 0):
            self.__class__.str_format = str_format

    def format(self):
        return self.__class__.str_format

    def packet_type(self):
        return PACKET_TYPES.index(type(self).__name__)

    def serialize(self):
        eval_str = f'struct.pack("!i" + self.format(), self.packet_type(), self.{", self.".join(self.__dict__.keys())})'
        print(eval_str)
        return \
            eval(eval_str)

    def inner_deserialize(self, info):
        for i in range(len(self.__dict__)):
            self.__setattr__(list(self.__dict__.keys())[i], info[i])

    @staticmethod
    def deserialize(bin_info):
        (packet_type,) = struct.unpack("!i", bin_info[:4])

        packet = eval(PACKET_TYPES[packet_type])()

        print(packet.format())
        print(len(bin_info[4:]), len(bin_info))

        others = struct.unpack("!" + packet.format(), bin_info[4:])

        packet.inner_deserialize(others)

        return packet


class SocketPacketList:
    def __init__(self, capacity: int = 0):
        self.capacity = capacity
        self.lock = Lock()
        self.packets = []

    def __len__(self):
        with self.lock:
            return len(self.packets)

    def pop(self):
        with self.lock:
            return self.packets.pop(0) if len(self) > 0 else None

    def push(self, packet: (bytes, (str, int))):
        with self.lock:
            if self.capacity and len(self.packets) == self.capacity:
                self.packets.pop(0)

            self.packets.append(packet)

    def serialize(self):
        with self.lock:
            result = bytearray(struct.pack("!i", len(self.packets)))

            for packet in self.packets:
                result.extend(packet.serialize())

        return result

    def deserialize(self, packet):
        return


# server packets
class PlayerEntityInfo(BasePacket):
    def __init__(self):
        super().__init__(
            ('x', 'f', 0.0),
            ('y', 'f', 0.0)
        )


# client packets
class PlayerInputInfo(BasePacket):
    def __init__(self):
        super().__init__(
            ('cursor_x', 'f', 0.0),
            ('cursor_y', 'f', 0.0),
            ('keys', 'i', 0)
        )


PACKET_TYPES = list(
    map(lambda p: p.__name__,
        [
            PlayerEntityInfo,

            PlayerInputInfo,
        ])
)
