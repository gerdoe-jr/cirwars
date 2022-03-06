import socket

from threading import Thread


class BaseNetwork:
    def __init__(self, net_info: (str, int), buffer_size: int):
        self.tcp = None
        self.udp = None

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

        if not self.tcp:
            self.tcp = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        if not self.udp:
            self.udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.tcp_thread = Thread(target=self.tcp_loop)
        self.tcp_thread.start()

        self.udp_thread = Thread(target=self.udp_loop)
        self.udp_thread.start()

    def stop(self):
        if self.running:
            self.tcp.close()
            self.udp.close()

            self.tcp = None
            self.udp = None

            self.tcp_thread = None
            self.udp_thread = None

        self.running = False

    def try_send(self, bin_info: bytes, to: (str, int) = None):
        try:
            self.udp.sendto(bin_info, to if to else self.net_info)
        except BlockingIOError:
            return
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)
            return

    def try_recv(self):
        try:
            return self.udp.recv(self.buffer_size)
        except BlockingIOError:
            return bytes()
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)
            return bytes()

    def try_recvfrom(self):
        try:
            return self.udp.recvfrom(self.buffer_size)
        except BlockingIOError:
            return bytes(), ('', 0)
        except Exception as e:
            print(f'(udp) ({e.__class__.__name__})', e)
            return bytes(), ('', 0)

    def tcp_loop(self):
        pass

    def udp_loop(self):
        pass
