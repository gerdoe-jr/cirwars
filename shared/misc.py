from os import path, listdir

from shared.globals import DATA_DIR


MAPS_DIR = DATA_DIR + 'maps/'


def load_map(map_name=None):
    name = map_name
    filename = ''

    if map_name:
        filename = MAPS_DIR + map_name
    else:
        for file in filter(lambda x: path.isfile(MAPS_DIR + x), listdir(MAPS_DIR)):
            name = file
            file = './data/maps/' + file
            if file.lower().rstrip().endswith('.tmap'):
                filename = file
                break

    if not filename:
        return None, None

    file = open(filename, 'r')
    data = file.readlines()
    file.close()
    return name, data
