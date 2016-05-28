from platform import system
import json
import os
import locale
from util import Singleton, curr_directory, log
import pyaudio
from toxencryptsave import LibToxEncryptSave


class Settings(Singleton, dict):
    """
    Settings of current profile + global app settings
    """

    def __init__(self, name):
        self.path = ProfileHelper.get_path() + str(name) + '.json'
        self.name = name
        if os.path.isfile(self.path):
            with open(self.path) as fl:
                data = fl.read()
            inst = LibToxEncryptSave.get_instance()
            if inst.has_password():
                data = inst.pass_decrypt(data)
            try:
                info = json.loads(data)
            except Exception as ex:
                info = Settings.get_default_settings()
                log('Parsing settings error: ' + str(ex))
            super(self.__class__, self).__init__(info)
            self.upgrade()
        else:
            super(self.__class__, self).__init__(Settings.get_default_settings())
            self.save()
        p = pyaudio.PyAudio()
        self.audio = {'input': p.get_default_input_device_info()['index'],
                      'output': p.get_default_output_device_info()['index']}

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
        """
        Default profile settings
        """
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
            'allow_auto_accept': True,
            'auto_accept_path': None,
            'show_online_friends': False,
            'auto_accept_from_friends': [],
            'friends_aliases': [],
            'typing_notifications': False,
            'calls_sound': True,
            'blocked': [],
            'plugins': []
        }

    @staticmethod
    def supported_languages():
        return [
            ('English', 'en_EN'),
            ('Russian', 'ru_RU'),
            ('French', 'fr_FR')
        ]

    def upgrade(self):
        default = Settings.get_default_settings()
        for key in default:
            if key not in self:
                print key
                self[key] = default[key]
        self.save()

    def save(self):
        text = json.dumps(self)
        inst = LibToxEncryptSave.get_instance()
        if inst.has_password():
            text = inst.pass_encrypt(text)
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
        """
        Mark current profile as active
        """
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


class ProfileHelper(Singleton):
    """
    Class with methods for search, load and save profiles
    """
    def __init__(self, path, name):
        path = path.decode(locale.getpreferredencoding())
        self._path = path + name + '.tox'
        self._directory = path
        # create /avatars if not exists:
        directory = path + 'avatars'
        if not os.path.exists(directory):
            os.makedirs(directory)

    def open_profile(self):
        with open(self._path, 'rb') as fl:
            data = fl.read()
        if data:
            return data
        else:
            raise IOError('Save file has zero size!')

    def get_dir(self):
        return self._directory

    def save_profile(self, data):
        inst = LibToxEncryptSave.get_instance()
        if inst.has_password():
            data = inst.pass_encrypt(data)
        with open(self._path, 'wb') as fl:
            fl.write(data)
        print 'Profile saved successfully'

    def export_profile(self, new_path):
        new_path += os.path.basename(self._path)
        with open(self._path, 'rb') as fin:
            data = fin.read()
        with open(new_path, 'wb') as fout:
            fout.write(data)
        print 'Profile exported successfully'

    @staticmethod
    def find_profiles():
        """
        Find available tox profiles
        """
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
        return False

    @staticmethod
    def get_path():
        return ProfileHelper.get_instance().get_dir()
