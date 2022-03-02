from shared.network import *
from shared.protocol import *
from shared.globals import *

from shared.event_handler import ClientEvents, EventReceiver, event_handler_instance


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)
        self.udp.setblocking(False)

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

                self.start()

        if len(self.received_packets):
            event_handler_instance.send(EventReceiver.GAME, ClientEvents.Game.NET_RECEIVED, self.received_packets.flush())

        if len(self.scheduled_packets):
            self.should_send = True

    def tcp_loop(self):
        try:
            self.tcp.connect(self.net_info)
            self.tcp.setblocking(False)
        except Exception as e:
            print(f'(tcp) ({e.__class__.__name__})', e)

        event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_CONNECTED)
        print('connected')

        while self.running:
            try:
                packet = self.tcp.recv(self.buffer_size)
                if packet:
                    self.received_packets.deserialize(packet)
                else:
                    break
            except BlockingIOError:
                continue
            except Exception as e:
                print(f'(tcp) ({e.__class__.__name__})', e)
                break

        self.tcp.close()
        self.stop()

        event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_DISCONNECTED)
        print('disconnected')

    def udp_loop(self):
        while self.running:
            if self.should_send:
                self.try_send(self.scheduled_packets.serialize())
                self.should_send = False

            packet = self.try_recv()
            if packet:
                self.received_packets.deserialize(packet)
                print(self.received_packets.packets)

        self.udp.close()
