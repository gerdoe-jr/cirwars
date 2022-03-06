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

        self.server.on_client_disconnect(self.net_info)
        self.stop()

    def udp_loop(self):
        pass


class NetworkServer(BaseNetwork):
    def __init__(self, port: int = NET_SERVER_PORT):
        super().__init__(('0.0.0.0', port), NET_BUF_SIZE)

        self.context = None

        self.lock = Lock()
        self.clients = {}
        self.ip_id_dict = {}

    def on_client_connect(self, connection, address):
        with self.lock:
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

    def on_client_receive(self, packet, address):
        client_id = self.ip_id_dict[address]
        self.clients[client_id].received_packets.deserialize(packet)
        for p in self.clients[client_id].received_packets.flush():
            if isinstance(p, ClientInputInfo):
                self.context.world.on_player_input(client_id, p)

    def on_client_disconnect(self, address):
        with self.lock:
            self.clients.pop(self.ip_id_dict[address])

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
                self.on_client_connect(*self.tcp.accept())
            except Exception as e:
                print(f'(tcp) ({e.__class__.__name__})', e)

        self.stop()

    def udp_loop(self):
        try:
            self.udp.bind(self.net_info)
            self.udp.setblocking(False)
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)

        while self.running:
            packet, address = self.try_recvfrom()
            if packet == b'':
                pass
            elif address in self.ip_id_dict.keys():
                self.on_client_receive(packet, address)

            with self.lock:
                for c in self.clients.values():
                    if len(c.scheduled_packets):
                        self.try_send(c.scheduled_packets.serialize(), c.net_info)

        self.stop()
