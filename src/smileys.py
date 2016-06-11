import util
import json
try:
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtCore


class SmileyLoader(util.Singleton):

    def __init__(self, settings):
        self.settings = settings
        self.curr_pack = None
        self.smiles = {}
        self.load_pack()

    def load_pack(self):
        pack_name = self.settings['smiley_pack']
        if self.settings['smileys'] and self.curr_pack != pack_name:
            self.curr_pack = pack_name
            path = self.get_smileys_path() + 'config.json'
            try:
                with open(path) as fl:
                    self.smiles = json.loads(fl.read())
                print 'Smiley pack', pack_name, 'loaded'
            except:
                print 'Smiley pack', pack_name, 'was not loaded'

    def get_smileys_path(self):
        return util.curr_directory() + '/smileys/' + self.curr_pack + '/'

    def add_smileys_to_text(self, text, edit):
        if not self.settings['smileys']:
            return text
        arr = text.split(' ')
        for i in range(len(arr)):
            if arr[i] in self.smiles:
                file_name = self.smiles[arr[i]]
                arr[i] = u'<img title=\"{}\" src=\"{}\" />'.format(arr[i], file_name)
                if file_name.endswith('.gif'):
                    edit.addAnimation(QtCore.QUrl(file_name), self.get_smileys_path() + file_name)
        return ' '.join(arr)
