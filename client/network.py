import time

from shared.network import *
from shared.protocol import *
from shared.globals import *


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

    def send_packet(self, packets):
        if isinstance(packets, BasePacket):
            self.scheduled_packets.push(packets.serialize())
        else:
            for packet in packets:
                self.scheduled_packets.push(packet.serialize())

    def main_thread(self):
        while self.running:
            while True:
                packet = self.scheduled_packets.pop()
                if packet:
                    self.try_send(packet, self.net_info)

                packet = self.try_recv()
                if packet == b'':
                    break
                elif packet:
                    self.received_packets.push(packet)
            self.socket.close()
