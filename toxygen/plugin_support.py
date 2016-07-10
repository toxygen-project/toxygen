import util
import profile
import os
import importlib
import inspect
import plugins.plugin_super_class as pl
import toxencryptsave
import sys


class PluginLoader(util.Singleton):

    def __init__(self, tox, settings):
        super().__init__()
        self._profile = profile.Profile.get_instance()
        self._settings = settings
        self._plugins = {}  # dict. key - plugin unique short name, value - tuple (plugin instance, is active)
        self._tox = tox
        self._encr = toxencryptsave.ToxEncryptSave.get_instance()

    def set_tox(self, tox):
        """
        New tox instance
        """
        self._tox = tox
        for value in self._plugins.values():
            value[0].set_tox(tox)

    def load(self):
        """
        Load all plugins in plugins folder
        """
        path = util.curr_directory() + '/plugins/'
        if not os.path.exists(path):
            util.log('Plugin dir not found')
            return
        else:
            sys.path.append(path)
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        for fl in files:
            if fl in ('plugin_super_class.py', '__init__.py') or not fl.endswith('.py'):
                continue
            name = fl[:-3]  # module name without .py
            try:
                module = importlib.import_module(name)  # import plugin
            except ImportError:
                util.log('Import error in module ' + name)
                continue
            except Exception as ex:
                util.log('Exception in module ' + name + ' Exception: ' + str(ex))
                continue
            for elem in dir(module):
                obj = getattr(module, elem)
                if inspect.isclass(obj) and hasattr(obj, 'is_plugin') and obj.is_plugin:  # looking for plugin class in module
                    print('Plugin', elem)
                    try:  # create instance of plugin class
                        inst = obj(self._tox, self._profile, self._settings, self._encr)
                        autostart = inst.get_short_name() in self._settings['plugins']
                        if autostart:
                            inst.start()
                    except Exception as ex:
                        util.log('Exception in module ' + name + ' Exception: ' + str(ex))
                        continue
                    self._plugins[inst.get_short_name()] = [inst, autostart]  # (inst, is active)
                    break

    def callback_lossless(self, friend_number, data, length):
        """
        New incoming custom lossless packet (callback)
        """
        l = data[0] - pl.LOSSLESS_FIRST_BYTE
        name = ''.join(chr(x) for x in data[1:l + 1])
        if name in self._plugins and self._plugins[name][1]:
            self._plugins[name][0].lossless_packet(''.join(chr(x) for x in data[l + 1:length]), friend_number)

    def callback_lossy(self, friend_number, data, length):
        """
        New incoming custom lossy packet (callback)
        """
        l = data[0] - pl.LOSSY_FIRST_BYTE
        name = ''.join(chr(x) for x in data[1:l + 1])
        if name in self._plugins and self._plugins[name][1]:
            self._plugins[name][0].lossy_packet(''.join(chr(x) for x in data[l + 1:length]), friend_number)

    def friend_online(self, friend_number):
        """
        Friend with specified number is online
        """
        for elem in self._plugins.values():
            if elem[1]:
                elem[0].friend_connected(friend_number)

    def get_plugins_list(self):
        """
        Returns list of all plugins
        """
        result = []
        for data in self._plugins.values():
            result.append([data[0].get_name(),  # plugin full name
                           data[1],  # is enabled
                           data[0].get_description(),  # plugin description
                           data[0].get_short_name()])  # key - short unique name
        return result

    def plugin_window(self, key):
        """
        Return window or None for specified plugin
        """
        return self._plugins[key][0].get_window()

    def toggle_plugin(self, key):
        """
        Enable/disable plugin
        :param key: plugin short name
        """
        plugin = self._plugins[key]
        if plugin[1]:
            plugin[0].stop()
        else:
            plugin[0].start()
        plugin[1] = not plugin[1]
        if plugin[1]:
            self._settings['plugins'].append(key)
        else:
            self._settings['plugins'].remove(key)
        self._settings.save()

    def command(self, text):
        """
        New command for plugin
        """
        text = text.strip()
        name = text.split()[0]
        if name in self._plugins and self._plugins[name][1]:
            self._plugins[name][0].command(text[len(name) + 1:])

    def get_menu(self, menu, num):
        """
        Return list of items for menu
        """
        result = []
        for elem in self._plugins.values():
            if elem[1]:
                try:
                    result.extend(elem[0].get_menu(menu, num))
                except:
                    continue
        return result

    def stop(self):
        """
        App is closing, stop all plugins
        """
        for key in list(self._plugins.keys()):
            if self._plugins[key][1]:
                self._plugins[key][0].close()
            del self._plugins[key]
