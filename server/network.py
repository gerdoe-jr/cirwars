from shared.network import BaseNetwork
from shared.protocol import *
from shared.globals import *


class ServerClient(BaseNetwork):
    def __init__(self, net_server, net_info: (str, int), tcp_connection):
        super().__init__(net_info, NET_BUF_SIZE)
        self.tcp = tcp_connection

        self.server = net_server

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

    def send_packets(self, packets):
        if isinstance(packets, BasePacket):
            self.scheduled_packets.push(packets)
        else:
            self.scheduled_packets.extend(packets)

    def tcp_loop(self):
        try:
            while self.running:
                if not self.tcp.recv(1):
                    break
        except Exception as e:
            print(f'(tcp) ({e.__class__.__name__})', e)
        finally:
            self.server.on_client_disconnect(self)
            self.tcp.close()
            self.stop()

    def udp_loop(self):
        while self.running:
            if len(self.scheduled_packets.packets):
                self.try_send(self.scheduled_packets.serialize(), self.net_info)
        self.udp.close()


class NetworkServer(BaseNetwork):
    def __init__(self, port: int = NET_SERVER_PORT):
        super().__init__(('0.0.0.0', port), NET_BUF_SIZE)

        self.context = None

        self.clients = {}
        self.ip_id_dict = {}

    def on_client_connect(self, connection, address):
        if address in self.ip_id_dict.keys():
            print(f'{address} have already connected')
            return

        available_ids = set(range(NET_MAX_CLIENTS)) - set(self.clients.keys())
        if not len(available_ids):
            print('server is full')
            return

        i = available_ids.pop()

        print(f"{address} connected")

        self.clients[i] = ServerClient(self, address, connection)
        self.clients[i].start()

        self.clients[i].send_packets(ServerInfo(self.map_name, len(self.clients), i))
        self.clients[i].tcp.send(SocketPacketList([ServerInfo(self.map_name, len(self.clients), i)]).serialize())

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

        print(f"{address} disconnected")

        self.context.world.on_player_disconnect(self.ip_id_dict.pop(address))

    def tcp_loop(self):
        try:
            self.tcp.bind(self.net_info)
            self.tcp.listen(NET_MAX_CLIENTS)
        except Exception as e:
            print(f'(tcp) ({e.__class__.__name__})', e)

        while self.running:
            try:
                connection, address = self.tcp.accept()
                self.on_client_connect(connection, address)
            except Exception as e:
                print(f'(tcp) ({e.__class__.__name__})', e)

        self.tcp.close()
        self.stop()

    def udp_loop(self):
        try:
            self.udp.bind(self.net_info)
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)

        while self.running:
            packet, address = self.try_recvfrom()
            if packet is None:
                continue
            elif address in self.ip_id_dict.keys():
                self.on_client_receive(address, packet)

        self.udp.close()
