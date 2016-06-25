import os
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


MAX_SHORT_NAME_LENGTH = 5

LOSSY_FIRST_BYTE = 200

LOSSLESS_FIRST_BYTE = 160


def path_to_data(name):
    """
    :param name: plugin unique name
    :return path do plugin's directory
    """
    return os.path.dirname(os.path.realpath(__file__)) + '/' + name + '/'


def log(name, data):
    """
    :param name: plugin unique name
    :param data: data for saving in log
    """
    with open(path_to_data(name) + 'logs.txt', 'a') as fl:
        fl.write(bytes(data, 'utf-8') + b'\n')


class PluginSuperClass:
    """
    Superclass for all plugins. Plugin is python module with at least one class derived from PluginSuperClass.
    """
    is_plugin = True

    def __init__(self, name, short_name, tox=None, profile=None, settings=None, encrypt_save=None):
        """
        :param name: plugin full name
        :param short_name: plugin unique short name (length of short name should not exceed MAX_SHORT_NAME_LENGTH)
        :param tox: tox instance
        :param profile: profile instance
        :param settings: profile settings
        :param encrypt_save: LibToxEncryptSave instance.
        """
        self._settings = settings
        self._profile = profile
        self._tox = tox
        name = name.strip()
        short_name = short_name.strip()
        if not name or not short_name:
            raise NameError('Wrong name')
        self._name = name
        self._short_name = short_name[:MAX_SHORT_NAME_LENGTH]
        self._translator = None  # translator for plugin's GUI
        self._encrypt_save = encrypt_save

    # -----------------------------------------------------------------------------------------------------------------
    # Get methods
    # -----------------------------------------------------------------------------------------------------------------

    def get_name(self):
        """
        :return plugin full name
        """
        return self._name

    def get_short_name(self):
        """
        :return plugin unique (short) name
        """
        return self._short_name

    def get_description(self):
        """
        Should return plugin description
        """
        return self.__doc__

    def get_menu(self, menu, row_number):
        """
        This method creates items for menu which called on right click in list of friends
        :param menu: menu instance
        :param row_number: number of selected row in list of contacts
        :return list of QAction's
        """
        return []

    def get_window(self):
        """
        This method should return window for plugins with GUI or None
        """
        return None

    def set_tox(self, tox):
        """
        New tox instance
        """
        self._tox = tox

    # -----------------------------------------------------------------------------------------------------------------
    # Plugin was stopped, started or new command received
    # -----------------------------------------------------------------------------------------------------------------

    def start(self):
        """
        This method called when plugin was started
        """
        pass

    def stop(self):
        """
        This method called when plugin was stopped
        """
        pass

    def close(self):
        """
        App is closing
        """
        pass

    def command(self, command):
        """
        New command. On 'help' this method should provide user list of available commands
        :param command: string with command
        """
        if command == 'help':
            msgbox = QtGui.QMessageBox()
            title = QtGui.QApplication.translate("PluginWindow", "List of commands for plugin {}", None, QtGui.QApplication.UnicodeUTF8)
            msgbox.setWindowTitle(title.format(self._name))
            msgbox.setText(QtGui.QApplication.translate("PluginWindow", "No commands available", None, QtGui.QApplication.UnicodeUTF8))
            msgbox.exec_()

    # -----------------------------------------------------------------------------------------------------------------
    # Translations support
    # -----------------------------------------------------------------------------------------------------------------

    def load_translator(self):
        """
        This method loads translations for GUI
        """
        app = QtGui.QApplication.instance()
        langs = self._settings.supported_languages()
        curr_lang = self._settings['language']
        if curr_lang in langs:
            if self._translator is not None:
                app.removeTranslator(self._translator)
            self._translator = QtCore.QTranslator()
            lang_path = langs[curr_lang]
            self._translator.load(path_to_data(self._short_name) + lang_path)
            app.installTranslator(self._translator)

    # -----------------------------------------------------------------------------------------------------------------
    # Settings loading and saving
    # -----------------------------------------------------------------------------------------------------------------

    def load_settings(self):
        """
        This method loads settings of plugin and returns raw data
        """
        with open(path_to_data(self._short_name) + 'settings.json', 'rb') as fl:
            data = fl.read()
        return str(data, 'utf-8')

    def save_settings(self, data):
        """
        This method saves plugin's settings to file
        :param data: string with data
        """
        with open(path_to_data(self._short_name) + 'settings.json', 'wb') as fl:
            fl.write(bytes(data, 'utf-8'))

    # -----------------------------------------------------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------------------------------------------------

    def lossless_packet(self, data, friend_number):
        """
        Incoming lossless packet
        :param data: string with data
        :param friend_number: number of friend who sent packet
        """
        pass

    def lossy_packet(self, data, friend_number):
        """
        Incoming lossy packet
        :param data: string with data
        :param friend_number: number of friend who sent packet
        """
        pass

    def friend_connected(self, friend_number):
        """
        Friend with specified number is online now
        """
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # Custom packets sending
    # -----------------------------------------------------------------------------------------------------------------

    def send_lossless(self, data, friend_number):
        """
        This method sends lossless packet to friend
        Wrapper for self._tox.friend_send_lossless_packet
        Use it instead of direct using self._tox.friend_send_lossless_packet
        :return True on success
        """
        if data is None:
            data = ''
        try:
            return self._tox.friend_send_lossless_packet(friend_number,
                                                         bytes([ord(x) for x in
                                                                chr(len(self._short_name) + LOSSLESS_FIRST_BYTE) +
                                                                self._short_name + str(data)
                                                                ]))
        except:
            return False

    def send_lossy(self, data, friend_number):
        """
        This method sends lossy packet to friend
        Wrapper for self._tox.friend_send_lossy_packet
        Use it instead of direct using self._tox.friend_send_lossy_packet
        :return True on success
        """
        if data is None:
            data = ''
        try:
            return self._tox.friend_send_lossy_packet(friend_number,
                                                      bytes([ord(x) for x in
                                                             chr(len(self._short_name) + LOSSY_FIRST_BYTE) +
                                                             self._short_name + str(data)
                                                             ]))
        except:
            return False
