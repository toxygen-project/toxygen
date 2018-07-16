import utils.util as util
import os
import importlib
import inspect
import plugins.plugin_super_class as pl
import sys


class Plugin:

    def __init__(self, plugin, is_active):
        self._instance = plugin
        self._is_active = is_active

    def get_instance(self):
        return self._instance

    instance = property(get_instance)

    def get_is_active(self):
        return self._is_active

    def set_is_active(self, is_active):
        self._is_active = is_active

    is_active = property(get_is_active, set_is_active)


class PluginLoader:

    def __init__(self, settings, app):
        self._settings = settings
        self._app = app
        self._plugins = {}  # dict. key - plugin unique short name, value - Plugin instance

    def set_tox(self, tox):
        """
        New tox instance
        """
        for plugin in self._plugins.values():
            plugin.instance.set_tox(tox)

    def load(self):
        """
        Load all plugins in plugins folder
        """
        path = util.get_plugins_directory()
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
                # looking for plugin class in module
                if not inspect.isclass(obj) or not hasattr(obj, 'is_plugin') or not obj.is_plugin:
                    continue
                print('Plugin', elem)
                try:  # create instance of plugin class
                    instance = obj(self._app)
                    is_active = instance.get_short_name() in self._settings['plugins']
                    if is_active:
                        instance.start()
                except Exception as ex:
                    util.log('Exception in module ' + name + ' Exception: ' + str(ex))
                    continue
                self._plugins[instance.get_short_name()] = Plugin(instance, is_active)
                break

    def callback_lossless(self, friend_number, data):
        """
        New incoming custom lossless packet (callback)
        """
        l = data[0] - pl.LOSSLESS_FIRST_BYTE
        name = ''.join(chr(x) for x in data[1:l + 1])
        if name in self._plugins and self._plugins[name].is_active:
            self._plugins[name].instance.lossless_packet(''.join(chr(x) for x in data[l + 1:]), friend_number)

    def callback_lossy(self, friend_number, data):
        """
        New incoming custom lossy packet (callback)
        """
        l = data[0] - pl.LOSSY_FIRST_BYTE
        name = ''.join(chr(x) for x in data[1:l + 1])
        if name in self._plugins and self._plugins[name].is_active:
            self._plugins[name].instance.lossy_packet(''.join(chr(x) for x in data[l + 1:]), friend_number)

    def friend_online(self, friend_number):
        """
        Friend with specified number is online
        """
        for plugin in self._plugins.values():
            if plugin.is_active:
                plugin.instance.friend_connected(friend_number)

    def get_plugins_list(self):
        """
        Returns list of all plugins
        """
        result = []
        for plugin in self._plugins.values():
            try:
                result.append([plugin.instance.get_name(),  # plugin full name
                               plugin.is_active,  # is enabled
                               plugin.instance.get_description(),  # plugin description
                               plugin.instance.get_short_name()])  # key - short unique name
            except:
                continue

        return result

    def plugin_window(self, key):
        """
        Return window or None for specified plugin
        """
        return self._plugins[key].instance.get_window()

    def toggle_plugin(self, key):
        """
        Enable/disable plugin
        :param key: plugin short name
        """
        plugin = self._plugins[key]
        if plugin.is_active:
            plugin.instance.stop()
        else:
            plugin.instance.start()
        plugin.is_active = not plugin.is_active
        if plugin.is_active:
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
        if name in self._plugins and self._plugins[name].is_active:
            self._plugins[name].instance.command(text[len(name) + 1:])

    def get_menu(self, num):
        """
        Return list of items for menu
        """
        result = []
        for plugin in self._plugins.values():
            if not plugin.is_active:
                continue
            try:
                result.extend(plugin.instance.get_menu(num))
            except:
                continue
        return result

    def get_message_menu(self, menu, selected_text):
        result = []
        for plugin in self._plugins.values():
            if not plugin.is_active:
                continue
            try:
                result.extend(plugin.instance.get_message_menu(menu, selected_text))
            except:
                pass
        return result

    def stop(self):
        """
        App is closing, stop all plugins
        """
        for key in list(self._plugins.keys()):
            if self._plugins[key].is_active:
                self._plugins[key].instance.close()
            del self._plugins[key]

    def reload(self):
        print('Reloading plugins')
        self.stop()
        self.load()
