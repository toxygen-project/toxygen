from platform import system
import json
import os
from util import Singleton, curr_directory, log, copy, append_slash
import pyaudio
from toxes import ToxES
import smileys


class Settings(dict, Singleton):
    """
    Settings of current profile + global app settings
    """

    def __init__(self, name):
        Singleton.__init__(self)
        self.path = ProfileHelper.get_path() + str(name) + '.json'
        self.name = name
        if os.path.isfile(self.path):
            with open(self.path, 'rb') as fl:
                data = fl.read()
            inst = ToxES.get_instance()
            try:
                if inst.is_data_encrypted(data):
                    data = inst.pass_decrypt(data)
                info = json.loads(str(data, 'utf-8'))
            except Exception as ex:
                info = Settings.get_default_settings()
                log('Parsing settings error: ' + str(ex))
            super(Settings, self).__init__(info)
            self.upgrade()
        else:
            super(Settings, self).__init__(Settings.get_default_settings())
            self.save()
        smileys.SmileyLoader(self)
        self.locked = False
        self.closing = False
        self.unlockScreen = False
        p = pyaudio.PyAudio()
        input_devices = output_devices = 0
        for i in range(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            if device["maxInputChannels"]:
                input_devices += 1
            if device["maxOutputChannels"]:
                output_devices += 1
        self.audio = {'input': p.get_default_input_device_info()['index'] if input_devices else -1,
                      'output': p.get_default_output_device_info()['index'] if output_devices else -1,
                      'enabled': input_devices and output_devices}
        self.video = {'device': 0, 'width': 640, 'height': 480}

    @staticmethod
    def get_auto_profile():
        p = Settings.get_global_settings_path()
        if os.path.isfile(p):
            with open(p) as fl:
                data = fl.read()
            auto = json.loads(data)
            if 'path' in auto and 'name' in auto:
                return str(auto['path']), str(auto['name'])
        return '', ''

    @staticmethod
    def set_auto_profile(path, name):
        p = Settings.get_global_settings_path()
        if os.path.isfile(p):
            with open(p) as fl:
                data = fl.read()
            data = json.loads(data)
        else:
            data = {}
        data['path'] = str(path)
        data['name'] = str(name)
        with open(p, 'w') as fl:
            fl.write(json.dumps(data))

    @staticmethod
    def reset_auto_profile():
        p = Settings.get_global_settings_path()
        if os.path.isfile(p):
            with open(p) as fl:
                data = fl.read()
            data = json.loads(data)
        else:
            data = {}
        if 'path' in data:
            del data['path']
            del data['name']
        with open(p, 'w') as fl:
            fl.write(json.dumps(data))

    @staticmethod
    def is_active_profile(path, name):
        path = path + name + '.lock'
        return os.path.isfile(path)

    @staticmethod
    def get_default_settings():
        """
        Default profile settings
        """
        return {
            'theme': 'dark',
            'ipv6_enabled': True,
            'udp_enabled': True,
            'proxy_type': 0,
            'proxy_host': '127.0.0.1',
            'proxy_port': 9050,
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
            'sorting': 0,
            'auto_accept_from_friends': [],
            'paused_file_transfers': {},
            'resend_files': True,
            'friends_aliases': [],
            'show_avatars': False,
            'typing_notifications': False,
            'calls_sound': True,
            'blocked': [],
            'plugins': [],
            'notes': {},
            'smileys': True,
            'smiley_pack': 'default',
            'mirror_mode': False,
            'width': 920,
            'height': 500,
            'x': 400,
            'y': 400,
            'message_font_size': 14,
            'unread_color': 'red',
            'save_unsent_only': False,
            'compact_mode': False,
            'show_welcome_screen': True,
            'close_to_tray': False,
            'font': 'Times New Roman',
            'update': 1
        }

    @staticmethod
    def supported_languages():
        return {
            'English': 'en_EN',
            'French': 'fr_FR',
            'Russian': 'ru_RU',
            'Ukrainian': 'uk_UA'
        }

    @staticmethod
    def built_in_themes():
        return {
            'dark': '/styles/dark_style.qss',
            'default': '/styles/style.qss'
        }

    def upgrade(self):
        default = Settings.get_default_settings()
        for key in default:
            if key not in self:
                print(key)
                self[key] = default[key]
        self.save()

    def save(self):
        text = json.dumps(self)
        inst = ToxES.get_instance()
        if inst.has_password():
            text = bytes(inst.pass_encrypt(bytes(text, 'utf-8')))
        else:
            text = bytes(text, 'utf-8')
        with open(self.path, 'wb') as fl:
            fl.write(text)

    def close(self):
        profile_path = ProfileHelper.get_path()
        path = str(profile_path + str(self.name) + '.lock')
        if os.path.isfile(path):
            os.remove(path)

    def set_active_profile(self):
        """
        Mark current profile as active
        """
        profile_path = ProfileHelper.get_path()
        path = str(profile_path + str(self.name) + '.lock')
        with open(path, 'w') as fl:
            fl.write('active')

    def export(self, path):
        text = json.dumps(self)
        with open(path + str(self.name) + '.json', 'w') as fl:
            fl.write(text)

    def update_path(self):
        self.path = ProfileHelper.get_path() + self.name + '.json'

    @staticmethod
    def get_global_settings_path():
        return curr_directory() + '/toxygen.json'

    @staticmethod
    def get_default_path():
        if system() == 'Windows':
            return os.getenv('APPDATA') + '/Tox/'
        elif system() == 'Darwin':
            return os.getenv('HOME') + '/Library/Application Support/Tox/'
        else:
            return os.getenv('HOME') + '/.config/tox/'


class ProfileHelper(Singleton):
    """
    Class with methods for search, load and save profiles
    """
    def __init__(self, path, name):
        Singleton.__init__(self)
        path = append_slash(path)
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
        inst = ToxES.get_instance()
        if inst.has_password():
            data = inst.pass_encrypt(data)
        with open(self._path, 'wb') as fl:
            fl.write(data)
        print('Profile saved successfully')

    def export_profile(self, new_path, use_new_path):
        path = new_path + os.path.basename(self._path)
        with open(self._path, 'rb') as fin:
            data = fin.read()
        with open(path, 'wb') as fout:
            fout.write(data)
        print('Profile exported successfully')
        copy(self._directory + 'avatars', new_path + 'avatars')
        if use_new_path:
            self._path = new_path + os.path.basename(self._path)
            self._directory = new_path
            Settings.get_instance().update_path()

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
    def get_path():
        return ProfileHelper.get_instance().get_dir()
