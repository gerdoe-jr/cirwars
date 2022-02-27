from shared.network import *
from shared.protocol import *
from shared.globals import *

from client.core.event_handler import Events, EventReceiver, event_handler_instance


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)
        self.socket.setblocking(False)

        self.should_send = False

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

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

            if event == Events.Network.TRY_CONNECT:
                (nick, server_address) = args
                self.net_info = (server_address[0], NET_SERVER_PORT)
                if not server_address[1]:
                    event_handler_instance.send(EventReceiver.NETWORK, Events.Network.TRY_CONNECT, nick, self.net_info)

                packet = ClientInfo()
                packet.nick = nick

                self.scheduled_packets.push(packet)
                print(f'pushed {packet.format()}')

                self.start()

        if len(self.received_packets):
            pass
            # event_handler_instance.send()

        if len(self.scheduled_packets):
            self.should_send = True

    def main_thread(self):
        print('connected')
        event_handler_instance.send(EventReceiver.INTERACTION, Events.Interaction.NET_CONNECTED)

        while self.running:
            if self.should_send:
                print('sent', self.scheduled_packets.packets)
                self.try_send(self.scheduled_packets.serialize())
                self.should_send = False

            packet = self.try_recv()
            if packet:
                self.received_packets.deserialize(packet)
                print(self.received_packets.packets)
        print('disconnected')
        self.socket.close()
