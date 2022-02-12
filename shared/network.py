import socket

from threading import Thread


class BaseNetwork:
    def __init__(self, net_info: (str, int), buffer_size: int, connection: socket.socket = None):
        self.socket = connection if connection else socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.setblocking(False)  # use try-catch blocks for every recv/send

        self.net_info = net_info
        self.buffer_size = buffer_size

        self.running = False
        self.net_thread = Thread(target=self.main_thread)

    def start(self):
        self.running = True
        self.net_thread.start()

    def stop(self):
        self.running = False

    def try_send(self, bin_info: bytes, to: (str, int) = None):
        try:
            if to is None:
                self.socket.sendto(bin_info, self.net_info)
            else:
                self.socket.sendto(bin_info, to)
        except Exception as e:
            print(e)

    def try_recv(self):
        try:
            return self.socket.recv(self.buffer_size)
        except Exception:
            return 0

    def main_thread(self):
        pass
