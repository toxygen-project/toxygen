import util
import json
import os
from collections import OrderedDict
try:
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtCore


class SmileyLoader(util.Singleton):
    """
    Class which loads smileys packs and insert smileys into messages
    """

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self._curr_pack = None  # current pack name
        self._smileys = {}  # smileys dict. key - smiley (str), value - path to image (str)
        self._list = []  # smileys list without duplicates
        self.load_pack()

    def load_pack(self):
        """
        Loads smiley pack
        """
        pack_name = self._settings['smiley_pack']
        if self._settings['smileys'] and self._curr_pack != pack_name:
            self._curr_pack = pack_name
            path = self.get_smileys_path() + 'config.json'
            try:
                with open(path, encoding='utf8') as fl:
                    self._smileys = json.loads(fl.read())
                    fl.seek(0)
                    tmp = json.loads(fl.read(), object_pairs_hook=OrderedDict)
                print('Smiley pack {} loaded'.format(pack_name))
                keys, values, self._list = [], [], []
                for key, value in tmp.items():
                    value = self.get_smileys_path() + value
                    if value not in values:
                        keys.append(key)
                        values.append(value)
                self._list = list(zip(keys, values))
            except Exception as ex:
                self._smileys = {}
                self._list = []
                print('Smiley pack {} was not loaded. Error: {}'.format(pack_name, ex))

    def get_smileys_path(self):
        return util.curr_directory() + '/smileys/' + self._curr_pack + '/'

    def get_packs_list(self):
        d = util.curr_directory() + '/smileys/'
        return [x[1] for x in os.walk(d)][0]

    def get_smileys(self):
        return list(self._list)

    def add_smileys_to_text(self, text, edit):
        """
        Adds smileys to text
        :param text: message
        :param edit: MessageEdit instance
        :return text with smileys
        """
        if not self._settings['smileys'] or not len(self._smileys):
            return text
        arr = text.split(' ')
        for i in range(len(arr)):
            if arr[i] in self._smileys:
                file_name = self._smileys[arr[i]]  # image name
                arr[i] = '<img title=\"{}\" src=\"{}\" />'.format(arr[i], file_name)
                if file_name.endswith('.gif'):  # animated smiley
                    edit.addAnimation(QtCore.QUrl(file_name), self.get_smileys_path() + file_name)
        return ' '.join(arr)


def sticker_loader():
    """
    :return list of stickers
    """
    result = []
    d = util.curr_directory() + '/stickers/'
    keys = [x[1] for x in os.walk(d)][0]
    for key in keys:
        path = d + key + '/'
        files = filter(lambda f: f.endswith('.png'), os.listdir(path))
        files = map(lambda f: str(path + f), files)
        result.extend(files)
    return result
