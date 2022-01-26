import socket

from shared.network import BaseNetwork, SocketPacketList
from shared.protocol import BasePacket
from shared.globals import *


class ServerClient(BaseNetwork):
    def __init__(self, net_server, connection: socket.socket, net_info: (str, int)):
        super().__init__(net_info, NET_BUF_SIZE, connection)

        self.server = net_server

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

    def send_packets(self, packets):
        if isinstance(packets, BasePacket):
            self.scheduled_packets.push(packets.serialize())
        else:
            for packet in packets:
                self.scheduled_packets.push(packet.serialize())

    def recv_packets(self):
        return [BasePacket.deserialize(self.received_packets.pop()) for _ in range(len(self.received_packets))]

    def main_thread(self):
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

        self.server.on_client_disconnect(self)


class NetworkServer(BaseNetwork):
    def __init__(self, port: int = NET_SERVER_PORT):
        super().__init__(('0.0.0.0', port), NET_BUF_SIZE)

        self.clients = {}

    def on_client_connect(self, connection, address):
        i = 0
        while i not in self.clients.keys():
            i += 1

        self.clients[i] = ServerClient(self, connection, address)
        self.clients[i].start()

        print("{} connected", address)

    def on_client_disconnect(self, client: ServerClient):
        for k in self.clients.keys():
            if client == self.clients[k]:
                self.clients.pop(k)

        print("{} disconnected", client.net_info)

    def main_thread(self):
        try:
            self.socket.bind(self.net_info)
            self.socket.listen(NET_MAX_CLIENTS)

            while self.running:
                connection, address = self.socket.accept()
                self.on_client_connect(connection, address)

        except socket.error as e:
            print(e)

