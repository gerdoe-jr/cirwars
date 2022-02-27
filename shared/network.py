import socket

from threading import Thread


class BaseNetwork:
    def __init__(self, net_info: (str, int), buffer_size: int, connection: socket.socket = None):
        self.socket = connection if connection else socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # use try-catch blocks for every recv/send

        self.net_info = net_info
        self.buffer_size = buffer_size

        self.running = False
        self.net_thread = None

    def __del__(self):
        self.stop()

    def start(self):
        if self.running:
            return
        self.running = True
        self.net_thread = Thread(target=self.main_thread)
        self.net_thread.start()

    def stop(self):
        self.running = False
        self.net_thread = None

    def try_send(self, bin_info: bytes, to: (str, int) = None):
        try:
            self.socket.sendto(bin_info, to if to else self.net_info)
        except Exception as e:
            print(e.__class__.__name__, e)

    def try_recv(self):
        try:
            return self.socket.recv(self.buffer_size)
        except Exception as e:
            return bytes()

    def try_recvfrom(self):
        try:
            return self.socket.recvfrom(self.buffer_size)
        except Exception as e:
            return None, ('', 0)

    def main_thread(self):
        pass
