from .global_client import game_client
from .network import *

if __name__ == '__main__':
    # game_client.run()

    playerinfo = PlayerEntityInfo()
    print(playerinfo.__dict__)
    print(playerinfo.format())
    print(playerinfo.serialize())
    print(BasePacket.deserialize(playerinfo.serialize()))
    print(PlayerEntityInfo().__dict__)
