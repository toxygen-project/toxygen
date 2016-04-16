from platform import system
import json
import os
import locale
from util import Singleton, curr_directory


class Settings(Singleton, dict):

    def __init__(self, name=''):
        self.path = ProfileHelper.get_path() + str(name) + '.json'
        self.name = name
        if os.path.isfile(self.path):
            with open(self.path) as fl:
                data = fl.read()
            super(self.__class__, self).__init__(json.loads(data))
        else:
            super(self.__class__, self).__init__(Settings.get_default_settings())
            self.save()

    @staticmethod
    def get_auto_profile():
        path = Settings.get_default_path() + 'toxygen.json'
        if os.path.isfile(path):
            with open(path) as fl:
                data = fl.read()
            auto = json.loads(data)
            if 'path' in auto and 'name' in auto:
                return unicode(auto['path']), unicode(auto['name'])

    @staticmethod
    def set_auto_profile(path, name):
        p = Settings.get_default_path() + 'toxygen.json'
        data = json.dumps({'path': unicode(path.decode(locale.getpreferredencoding())), 'name': unicode(name)})
        with open(p, 'w') as fl:
               fl.write(data)

    @staticmethod
    def get_default_settings():
        return {
            'theme': 'default',
            'ipv6_enabled': True,
            'udp_enabled': True,
            'proxy_type': 0,
            'proxy_host': '0',
            'proxy_port': 0,
            'start_port': 0,
            'end_port': 0,
            'tcp_port': 0,
            'notifications': True,
            'sound_notifications': False,
            'language': 'English',
            'save_history': False,
            'allow_inline': True,
            'allow_auto_accept': False,
            'auto_accept_path': None,
            'show_online_friends': False,
            'auto_accept_from_friends': [],
            'friends_aliases': [],
            'typing_notifications': True,
            'calls_sound': True
        }

    @staticmethod
    def supported_languages():
        return [
            ('English', 'en_EN'),
            ('Russian', 'ru_RU'),
            ('French', 'fr_FR')
        ]

    def save(self):
        text = json.dumps(self)
        with open(self.path, 'w') as fl:
            fl.write(text)

    def close(self):
        path = Settings.get_default_path() + 'toxygen.json'
        if os.path.isfile(path):
            with open(path) as fl:
                data = fl.read()
            app_settings = json.loads(data)
            try:
                app_settings['active_profile'].remove(unicode(ProfileHelper.get_path() + self.name + '.tox'))
            except:
                pass
            data = json.dumps(app_settings)
            with open(path, 'w') as fl:
                fl.write(data)

    def set_active_profile(self):
        path = Settings.get_default_path() + 'toxygen.json'
        if os.path.isfile(path):
            with open(path) as fl:
                data = fl.read()
            app_settings = json.loads(data)
        else:
            app_settings = {}
        if 'active_profile' not in app_settings:
            app_settings['active_profile'] = []
        profile_path = ProfileHelper.get_path()
        app_settings['active_profile'].append(unicode(profile_path + str(self.name) + '.tox'))
        data = json.dumps(app_settings)
        with open(path, 'w') as fl:
            fl.write(data)

    def export(self, path):
        text = json.dumps(self)
        with open(path + str(self.name) + '.json', 'w') as fl:
            fl.write(text)

    @staticmethod
    def get_default_path():
        if system() == 'Linux':
            return os.getenv('HOME') + '/.config/tox/'
        elif system() == 'Windows':
            return os.getenv('APPDATA') + '/Tox/'


class ProfileHelper(object):
    """
    Class with static methods for search, load and save profiles
    """
    @staticmethod
    def find_profiles():
        path = Settings.get_default_path()
        result = []
        # check default path
        if not os.path.exists(path):
            os.makedirs(path)
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        path = curr_directory()
        # check current directory
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path + '/', name))
        return result

    @staticmethod
    def is_active_profile(path, name):
        path = path.decode(locale.getpreferredencoding()) + name + '.tox'
        settings = Settings.get_default_path() + 'toxygen.json'
        if os.path.isfile(settings):
            with open(settings) as fl:
                data = fl.read()
            data = json.loads(data)
            if 'active_profile' in data:
                return path in data['active_profile']
        else:
            return False

    @staticmethod
    def open_profile(path, name):
        path = path.decode(locale.getpreferredencoding())
        ProfileHelper._path = path + name + '.tox'
        ProfileHelper._directory = path
        with open(ProfileHelper._path, 'rb') as fl:
            data = fl.read()
        if data:
            return data
        else:
            raise IOError('Save file has zero size!')

    @staticmethod
    def save_profile(data, name=None):
        if name is not None:
            ProfileHelper._path = Settings.get_default_path() + name + '.tox'
            ProfileHelper._directory = Settings.get_default_path()
        with open(ProfileHelper._path, 'wb') as fl:
            fl.write(data)

    @staticmethod
    def export_profile(new_path):
        new_path += os.path.basename(ProfileHelper._path)
        with open(ProfileHelper._path, 'rb') as fin:
            data = fin.read()
        with open(new_path, 'wb') as fout:
            fout.write(data)
        print 'Data exported to: {}'.format(new_path)

    @staticmethod
    def get_path():
        return ProfileHelper._directory
