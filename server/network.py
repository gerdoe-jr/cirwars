from shared.network import BaseNetwork
from shared.protocol import *
from shared.globals import *


class ServerClient(BaseNetwork):
    def __init__(self, net_server, net_info: (str, int)):
        super().__init__(net_info, NET_BUF_SIZE)
        self.socket.settimeout(1.0)

        self.server = net_server

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
            if len(self.scheduled_packets.packets):
                self.try_send(self.scheduled_packets.serialize(), self.net_info)
        self.socket.close()
        print('stopped client')


class NetworkServer(BaseNetwork):
    def __init__(self, port: int = NET_SERVER_PORT):
        super().__init__(('0.0.0.0', port), NET_BUF_SIZE)

        self.context = None

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

        self.clients[i].send_packets(ServerInfo(self.map_name, len(self.clients), i))

        self.ip_id_dict[address] = i

        self.context.world.on_player_connect(i)

    def on_client_receive(self, address, packet):
        client_id = self.ip_id_dict[address]
        slist = self.clients[client_id].received_packets
        slist.deserialize(packet)

        for p in slist.packets:
            if isinstance(p, ClientInputInfo):
                self.context.world.on_player_input(client_id, p)

        slist.packets.clear()

    def on_client_disconnect(self, client: ServerClient):
        address = client.net_info
        self.clients.pop(self.ip_id_dict[address]).stop()

        print(f"{client.net_info} disconnected")

        self.context.world.on_player_disconnect(self.ip_id_dict.pop(address))

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
                if packet == b'':
                    self.on_client_disconnect(self.clients[self.ip_id_dict[address]])
                else:
                    self.on_client_receive(address, packet)
            else:
                self.on_client_connect(address)
