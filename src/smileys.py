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
        self.settings = settings
        self.curr_pack = None  # current pack name
        self.smileys = {}  # smileys dict. key - smiley (str), value - path to image (str)
        self.load_pack()

    def load_pack(self):
        """
        Loads smiley pack
        """
        pack_name = self.settings['smiley_pack']
        if self.settings['smileys'] and self.curr_pack != pack_name:
            self.curr_pack = pack_name
            path = self.get_smileys_path() + 'config.json'
            try:
                with open(path) as fl:
                    self.smileys = json.loads(fl.read())
                print 'Smiley pack', pack_name, 'loaded'
            except:
                print 'Smiley pack', pack_name, 'was not loaded'

    def get_smileys_path(self):
        return util.curr_directory() + '/smileys/' + self.curr_pack + '/'

    def get_packs_list(self):
        d = util.curr_directory() + '/smileys/'
        return [x[1] for x in os.walk(d)][0]

    def add_smileys_to_text(self, text, edit):
        """
        Adds smileys to text
        :param text: message
        :param edit: MessageEdit instance
        :return text with smileys
        """
        if not self.settings['smileys']:
            return text
        arr = text.split(' ')
        for i in range(len(arr)):
            if arr[i] in self.smileys:
                file_name = self.smileys[arr[i]]  # image name
                arr[i] = u'<img title=\"{}\" src=\"{}\" />'.format(arr[i], file_name)
                if file_name.endswith('.gif'):  # animated smiley
                    edit.addAnimation(QtCore.QUrl(file_name), self.get_smileys_path() + file_name)
        return ' '.join(arr)
