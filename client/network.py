import time

from shared.network import *
from shared.globals import *


class NetworkClient(BaseNetwork):
    def __init__(self, server_address: str = '127.0.0.1', server_port: int = NET_SERVER_PORT):
        super().__init__((server_address, server_port), NET_BUF_SIZE)

    def main_thread(self):
        while self.running:
            time.sleep(2)
