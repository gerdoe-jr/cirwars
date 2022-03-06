from shared.network import *
from shared.protocol import *
from shared.globals import *

from shared.event_handler import ClientEvents, EventReceiver, event_handler_instance

import time


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)

        self.should_send = False
        self.connected = False

        self.scheduled_packets = SocketPacketList()
        self.received_packets = SocketPacketList()

        self.ticks = TICK_SPEED

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
                # self.should_send = True

                self.start()

        if self.running:
            self.ticks -= 1
            if not self.ticks:
                self.scheduled_packets.push(ClientAlive())
                self.ticks = TICK_SPEED // 2

        if len(self.received_packets.packets):
            event_handler_instance.send(EventReceiver.GAME, ClientEvents.Game.NET_RECEIVED, self.received_packets.flush())

        if len(self.scheduled_packets.packets):
            self.should_send = True

    def tcp_loop(self):
        try:
            self.tcp.connect(self.net_info)
            self.udp.bind(self.tcp.getsockname())

            self.connected = True
        except Exception as e:
            print(f'(tcp) ({e.__class__.__name__})', e)
            event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_FAILED)
            self.stop()
            self.connected = False
            return

        print('connected')

        while self.running:
            try:
                packet = self.tcp.recv(256)
                if packet:
                    self.received_packets.deserialize(packet)
                    print(self.received_packets.packets)

                    event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_CONNECTED)
                else:
                    break

                time.sleep(2)
            except BlockingIOError:
                continue
            except Exception as e:
                print(f'(tcp) ({e.__class__.__name__})', e)
                break

        event_handler_instance.send(EventReceiver.INTERACTION, ClientEvents.Interaction.NET_DISCONNECTED)
        print('(tcp) disconnected')

        self.connected = False

        self.stop()

    def udp_loop(self):
        while not (self.connected and self.should_send):
            pass

        while self.running:
            if self.should_send:
                self.try_send(self.scheduled_packets.serialize())
                self.should_send = False

            packet = self.try_recvfrom()[0]
            if packet != b'':
                self.received_packets.deserialize(packet)

        self.stop()
        print('(udp) disconnected')
