import struct
from threading import Lock


class BasePacket:
    def __init__(self, *attrs):
        str_format = ''

        for attr in attrs:
            self.__setattr__(attr[0], attr[2])
            str_format += attr[1]

        if not getattr(self, "str_format", 0):  # never initialize parent class object
            self.__class__.str_format = str_format

    def format(self):
        return self.__class__.str_format

    def packet_type(self):
        return PACKET_TYPES.index(type(self).__name__)

    def serialize(self):
        for e in self.__dict__.keys():
            if isinstance(self.__getattribute__(e), str):
                self.__setattr__(e, str.encode(self.__getattribute__(e)))
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

        bin_info = bin_info[4:4 + struct.calcsize(packet.format()) + 1]

        print(packet.format())

        others = struct.unpack("!" + packet.format(), bin_info)

        packet.inner_deserialize(others)

        return packet


class SocketPacketList:
    def __init__(self):
        self.lock = Lock()
        self.packets = []

    def __len__(self):
        with self.lock:
            return len(self.packets)

    def pop(self):
        with self.lock:
            return self.packets.pop(0) if len(self.packets) else None

    def push(self, packet):
        with self.lock:
            self.packets.append(packet)

    def extend(self, packets):
        with self.lock:
            self.packets.extend(packets)

    def serialize(self):
        with self.lock:
            result = bytearray(struct.pack("!i", len(self.packets)))

            for _ in range(len(self.packets)):
                result.extend(self.packets.pop(0).serialize())

        return result

    def deserialize(self, raw_packet):
        with self.lock:
            (length,) = struct.unpack("!i", raw_packet[:4])
            raw_packet = raw_packet[4:]
            for _ in range(length):
                packet = BasePacket.deserialize(raw_packet)
                self.packets.append(packet)

                raw_packet = raw_packet[struct.calcsize(packet.format()) :]


# server packets
class PlayerEntityInfo(BasePacket):
    def __init__(self):
        super().__init__(
            ('x', 'f', 0.0),
            ('y', 'f', 0.0)
        )


# ####


# client packets
class ClientInfo(BasePacket):
    def __init__(self):
        super().__init__(
            ('nick', '8s', '')
        )


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

            ClientInfo,
            PlayerInputInfo,
        ])
)
