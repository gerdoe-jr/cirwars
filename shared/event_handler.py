class EventReceiver:
    GAME = 0
    INTERACTION = 1
    NETWORK = 2

    RECEIVER_NUM = 3


class ClientEvents:
    class Game:
        START = 0
        STOP = 1

        NET_RECEIVED = 2

    class Interaction:
        NET_CONNECTED = 0
        NET_DISCONNECTED = 1
        NET_RECEIVED = 2

    class Network:
        TRY_CONNECT = 0
        TRY_DISCONNECT = 1

        TRY_SEND = 2


class EventHandler:
    def __init__(self):
        self.events = [[] for _ in range(EventReceiver.RECEIVER_NUM)]

    def recv(self, event_receiver):
        return self.events[event_receiver].pop(0) if len(self.events[event_receiver]) else None

    def send(self, event_receiver, event, *args):
        self.events[event_receiver].append((event, args))


event_handler_instance = EventHandler()
