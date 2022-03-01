from shared.network import *
from shared.protocol import *
from shared.globals import *

from shared.event_handler import ClientEvents, EventReceiver, event_handler_instance


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)
        self.socket.setblocking(False)

        self.should_send = False

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

        self.map_name = ''
        self.client_id = 0

    def send_packet(self, packets):
        if isinstance(packets, BasePacket):
            self.scheduled_packets.push(packets)
        else:
            self.scheduled_packets.extend(packets)

    def on_tick(self):
        event = event_handler_instance.recv(EventReceiver.NETWORK)

        if event:
            event, args = event

            print(event, args)

            if event == ClientEvents.Network.TRY_CONNECT:
                (nick, server_address) = args
                self.net_info = (server_address[0], NET_SERVER_PORT)

                packet = ClientInfo()
                packet.nick = nick

                self.scheduled_packets.push(packet)
                print(f'pushed {packet.format()}')

                self.start()

        if len(self.received_packets):
            event_handler_instance.send(EventReceiver.GAME, ClientEvents.Game.NET_RECEIVED, self.received_packets.flush())

        if len(self.scheduled_packets):
            self.should_send = True

    def main_thread(self):
        connected = False

        while not connected:
            if self.should_send:
                self.try_send(self.scheduled_packets.serialize())
                self.should_send = False

            packet = self.try_recv()
            if packet:
                self.received_packets.deserialize(packet)
                with self.received_packets.lock:
                    for p in self.received_packets.packets:
                        if isinstance(p, ServerInfo):
                            self.map_name = p.map_name.decode('utf-8').rstrip('\x00')
                            self.client_id = p.client_id
                            connected = True
                            break

        event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_CONNECTED)
        print('connected')

        while self.running:
            if self.should_send:
                self.try_send(self.scheduled_packets.serialize())
                self.should_send = False

            packet = self.try_recv()
            if packet:
                self.received_packets.deserialize(packet)
                # print(list(map(lambda x: x.__dict__, self.received_packets.packets)))

        print('disconnected')
        self.socket.close()

        event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_DISCONNECTED)
