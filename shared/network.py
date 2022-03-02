import socket

from threading import Thread
from time import sleep


class BaseNetwork:
    def __init__(self, net_info: (str, int), buffer_size: int):
        self.tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.net_info = net_info
        self.buffer_size = buffer_size

        self.running = False
        self.tcp_thread = None
        self.udp_thread = None

    def __del__(self):
        self.stop()

    def start(self):
        if self.running:
            return
        self.running = True

        self.tcp_thread = Thread(target=self.tcp_loop)
        self.tcp_thread.start()

        self.udp_thread = Thread(target=self.udp_loop)
        self.udp_thread.start()

    def stop(self):
        self.running = False
        self.tcp_thread = None
        self.udp_thread = None

    def try_send(self, bin_info: bytes, to: (str, int) = None):
        try:
            self.udp.sendto(bin_info, to if to else self.net_info)
        except socket.error as e:
            print(e.__class__.__name__, e)

    def try_recv(self):
        try:
            return self.udp.recv(self.buffer_size)
        except Exception as e:
            return bytes()

    def try_recvfrom(self):
        try:
            return self.udp.recvfrom(self.buffer_size)
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)
            return None, ('', 0)

    def tcp_loop(self):
        pass

    def udp_loop(self):
        pass
