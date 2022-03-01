import struct
from threading import Lock

PACKET_TYPES = []


def new_packet(name, *attributes):
    PACKET_TYPES.append(name)
    index = len(PACKET_TYPES) - 1

    init_attrs = ", ".join([f'{a[0]}=' + (f'{a[2]}' if not isinstance(a[2], str) else f"'{a[2]}'") for a in attributes])

    compile_str = f'''def i_func(ins, {init_attrs}):
    {" ; ".join([f"ins.{a[0]} = {a[0]}" for a in attributes])}'''

    exec(compile(compile_str, '', 'exec'))

    type_dict = {a[0]: a[2] for a in attributes}

    type_dict['init'] = eval('i_func')
    type_dict['packet_type'] = lambda self: index
    type_dict['str_format'] = ''.join(map(lambda a: a[1], attributes))

    return type(name, (BasePacket,), type_dict)


class BasePacket:
    attributes = []
    str_format = ''

    def __init__(self, *args, **kwargs):
        type(self).init(self, *args, **kwargs)

    def format(self):
        return type(self).str_format

    def packet_type(self):
        pass

    def serialize(self):
        for e in self.__dict__.keys():
            if isinstance(self.__getattribute__(e), str):
                self.__setattr__(e, str.encode(self.__getattribute__(e)))
        eval_str = f'struct.pack("!i" + self.format(), self.packet_type(), self.{", self.".join(self.__dict__.keys())})'
        return \
            eval(eval_str)

    def inner_deserialize(self, info):
        for i in range(len(self.__dict__)):
            self.__setattr__(list(self.__dict__.keys())[i], info[i])

    @staticmethod
    def deserialize(bin_info):
        (packet_type,) = struct.unpack("!i", bin_info[:4])

        packet = eval(PACKET_TYPES[packet_type])()

        bin_info = bin_info[4:4 + struct.calcsize(packet.format())]
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

    def flush(self):
        with self.lock:
            packets = self.packets[:]
            self.packets.clear()
        return packets

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

                raw_packet = raw_packet[4 + struct.calcsize(packet.format()):]


# server packets
PlayerEntityInfo = new_packet('PlayerEntityInfo',
                              ('client_id', 'i', 0),
                              ('x', 'f', 0.0),
                              ('y', 'f', 0.0)
                              )

ServerInfo = new_packet('ServerInfo',
                        ('map_name', '64s', ''),
                        ('player_amount', 'i', 0),
                        ('client_id', 'i', 0)
                        )

PlayerSpawnInfo = new_packet('PlayerSpawnInfo',
                             ('client_id', 'i', 0)
                             )

PlayerDeathInfo = new_packet('PlayerDeathInfo',
                             ('client_id', 'i', 0)
                             )

# ####


# client packets
ClientInfo = new_packet('ClientInfo',
                        ('nick', '8s', 'noname')
                        )

ClientInputInfo = new_packet('ClientInputInfo',
                             ('cursor_x', 'f', 0.0),
                             ('cursor_y', 'f', 0.0),
                             ('keys', 'i', 0)
                             )
