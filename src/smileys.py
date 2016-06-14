import util
import json
import os
try:
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtCore


class SmileyLoader(util.Singleton):
    """
    Class which loads smileys packs and insert smileys into messages
    """

    def __init__(self, settings):
        self._settings = settings
        self._curr_pack = None  # current pack name
        self._smileys = {}  # smileys dict. key - smiley (str), value - path to image (str)
        self._set = {}  # smileys dict without duplicates
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
                with open(path) as fl:
                    self._smileys = json.loads(fl.read())
                print 'Smiley pack', pack_name, 'loaded'
                self._set = {}
                for key, value in self._smileys.items():
                    value = self.get_smileys_path() + value
                    if value not in self._set.values():
                        self._set[key] = value
            except:
                self._smileys = {}
                self._set = {}
                print 'Smiley pack', pack_name, 'was not loaded'

    def get_smileys_path(self):
        return util.curr_directory() + '/smileys/' + self._curr_pack + '/'

    def get_packs_list(self):
        d = util.curr_directory() + '/smileys/'
        return [x[1] for x in os.walk(d)][0]

    def get_smileys(self):
        return list(self._set.items())

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
                arr[i] = u'<img title=\"{}\" src=\"{}\" />'.format(arr[i], file_name)
                if file_name.endswith('.gif'):  # animated smiley
                    edit.addAnimation(QtCore.QUrl(file_name), self.get_smileys_path() + file_name)
        return ' '.join(arr)


def sticker_loader():
    """
    :return dict of stickers
    """
    result = {}
    d = util.curr_directory() + '/stickers/'
    keys = [x[1] for x in os.walk(d)][0]
    for key in keys:
        path = d + key
        files = map(lambda f: f.endswith('.png'), os.listdir(path))
        if files:
            result[key] = files
    return result
