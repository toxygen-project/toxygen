import json
from utils.util import *
import pyaudio
from common.event import Event


class Settings(dict):
    """
    Settings of current profile + global app settings
    """

    def __init__(self, toxes, path):
        self._path = path
        self._profile_path = path.replace('.json', '.tox')
        self._toxes = toxes
        self._settings_saved_event = Event()
        if os.path.isfile(path):
            with open(path, 'rb') as fl:
                data = fl.read()
            try:
                if toxes.is_data_encrypted(data):
                    data = toxes.pass_decrypt(data)
                info = json.loads(str(data, 'utf-8'))
            except Exception as ex:
                info = Settings.get_default_settings()
                log('Parsing settings error: ' + str(ex))
            super().__init__(info)
            self._upgrade()
        else:
            super().__init__(Settings.get_default_settings())
        self.save()
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
        self.video = {'device': -1, 'width': 640, 'height': 480, 'x': 0, 'y': 0}

    # -----------------------------------------------------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------------------------------------------------

    def get_settings_saved_event(self):
        return self._settings_saved_event

    settings_saved_event = property(get_settings_saved_event)

    # -----------------------------------------------------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------------------------------------------------

    def save(self):
        text = json.dumps(self)
        if self._toxes.has_password():
            text = bytes(self._toxes.pass_encrypt(bytes(text, 'utf-8')))
        else:
            text = bytes(text, 'utf-8')
        with open(self._path, 'wb') as fl:
            fl.write(text)

        self._settings_saved_event(text)

    def close(self):
        path = self._profile_path + '.lock'
        if os.path.isfile(path):
            os.remove(path)

    def set_active_profile(self):
        """
        Mark current profile as active
        """
        path = self._profile_path + '.lock'
        with open(path, 'w') as fl:
            fl.write('active')

    def export(self, path):
        text = json.dumps(self)
        name = os.path.basename(self._path)
        with open(join_path(path, str(name)), 'w') as fl:
            fl.write(text)

    def update_path(self, new_path):
        self._path = new_path
        self.save()

    # -----------------------------------------------------------------------------------------------------------------
    # Static methods
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_auto_profile():
        p = Settings.get_global_settings_path()
        if not os.path.isfile(p):
            return None
        with open(p) as fl:
            data = fl.read()
        try:
            auto = json.loads(data)
        except Exception as ex:
            log(str(ex))
            auto = {}
        if 'profile_path' in auto:
            path = str(auto['profile_path'])
            if not os.path.isabs(path):
                path = join_path(path, curr_directory(__file__))
            if os.path.isfile(path):
                return path

    @staticmethod
    def set_auto_profile(path):
        p = Settings.get_global_settings_path()
        if os.path.isfile(p):
            with open(p) as fl:
                data = fl.read()
            data = json.loads(data)
        else:
            data = {}
        data['profile_path'] = str(path)
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
        if 'profile_path' in data:
            del data['profile_path']
        with open(p, 'w') as fl:
            fl.write(json.dumps(data))

    @staticmethod
    def is_active_profile(profile_path):
        return os.path.isfile(profile_path + '.lock')

    @staticmethod
    def get_default_settings():
        """
        Default profile settings
        """
        return {
            'theme': 'dark',
            'ipv6_enabled': False,
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
            'identicons': True,
            'show_welcome_screen': True,
            'close_app': 0,
            'font': 'Times New Roman',
            'update': 1,
            'group_notifications': True,
            'download_nodes_list': False,
            'notify_all_gc': False,
            'lan_discovery': True,
            'backup_directory': None
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
            'dark': 'dark_style.qss',
            'default': 'style.qss'
        }

    @staticmethod
    def get_global_settings_path():
        return os.path.join(get_base_directory(), 'toxygen.json')

    @staticmethod
    def get_default_path():
        system = get_platform()
        if system == 'Windows':
            return os.getenv('APPDATA') + '/Tox/'
        elif system == 'Darwin':
            return os.getenv('HOME') + '/Library/Application Support/Tox/'
        else:
            return os.getenv('HOME') + '/.config/tox/'

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _upgrade(self):
        default = Settings.get_default_settings()
        for key in default:
            if key not in self:
                print(key)
                self[key] = default[key]
