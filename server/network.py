from shared.network import BaseNetwork
from shared.protocol import BasePacket, SocketPacketList
from shared.globals import *


class ServerClient(BaseNetwork):
    def __init__(self, net_server, net_info: (str, int)):
        super().__init__(net_info, NET_BUF_SIZE)

        self.server = net_server
        self.socket.settimeout(1.0)

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

    def send_packets(self, packets):
        if isinstance(packets, BasePacket):
            self.scheduled_packets.push(packets)
        else:
            self.scheduled_packets.extend(packets)

    def main_thread(self):
        print('started client')
        while self.running:
            if len(self.scheduled_packets):
                self.try_send(self.scheduled_packets.serialize(), self.net_info)
        self.socket.close()
        print('stopped client')

        self.server.on_client_disconnect(self)


class NetworkServer(BaseNetwork):
    def __init__(self, port: int = NET_SERVER_PORT):
        super().__init__(('0.0.0.0', port), NET_BUF_SIZE)

        self.clients = {}
        self.ip_id_dict = {}

    def on_client_connect(self, address):
        if address in self.ip_id_dict.keys():
            print(f'{address} had already connected')
            return

        available_ids = set(range(NET_MAX_CLIENTS)) - set(self.clients.keys())
        if not len(available_ids):
            print('server is full')
            return

        i = available_ids.pop()

        print(f"{address} connected")

        self.clients[i] = ServerClient(self, address)
        self.clients[i].start()

        self.ip_id_dict[address] = i

    def on_client_receive(self, address, packet):
        self.clients[self.ip_id_dict[address]].received_packets.deserialize(packet)

    def on_client_disconnect(self, client: ServerClient):
        address = client.net_info
        self.clients.pop(self.ip_id_dict[address])
        self.ip_id_dict.pop(address)

        print(f"{client.net_info} disconnected")

    def main_thread(self):
        try:
            self.socket.bind(self.net_info)
        except Exception as e:
            print('[NET]', e.__class__.__name__, e)

        while self.running:
            packet, address = self.try_recvfrom()
            if packet is None:
                continue
            elif address in self.ip_id_dict.keys():
                self.on_client_receive(address, packet)
            else:
                self.on_client_connect(address)
