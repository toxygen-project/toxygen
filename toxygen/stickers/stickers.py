import os
import util.util as util


def load_stickers():
    """
    :return list of stickers
    """
    result = []
    d = util.get_stickers_directory()
    keys = [x[1] for x in os.walk(d)][0]
    for key in keys:
        path = d + key + '/'
        files = filter(lambda f: f.endswith('.png'), os.listdir(path))
        files = map(lambda f: str(path + f), files)
        result.extend(files)

    return result
