#Plugins API

In Toxygen plugin is single python (supported Python 3.0 - 3.4) module (.py file) and directory with data associated with it. 
Every module must contain one class derived from PluginSuperClass defined in [plugin_super_class.py](/src/plugins/plugin_super_class.py). Instance of this class will be created by PluginLoader class (defined in [plugin_support.py](/src/plugin_support.py) ). This class can enable/disable plugins and send data to it. 

Every plugin has its own full name and unique short name (1-5 symbols). Main app can get it using special methods. 

All plugin's data should be stored in following structure:

```
/plugins/
|---plugin_short_name.py
|---/plugin_short_name/
	|---settings.json
	|---logs.txt
	|---other_files
```

Plugin MUST override:
-  __init__ with params: tox (Tox instance), profile (Profile instance), settings (Settings instance), encrypt_save (ToxEncryptSave instance). Call super().__init__ with params plugin_full_name, plugin_short_name, tox, profile, settings, encrypt_save.

Plugin can override following methods:
- get_description - this method should return plugin description. 
- get_menu - plugins allowed to add items in friend menu. User can open this menu making right click on friend in friends list. This method should return list of QAction's. Plugin must connect to QAction's triggered() signal. 
- get_window - plugins can have GUI, this method should return window instance or None for plugins without GUI.
- start - plugin was started.
- stop - plugin was stopped.
- close - app is closing, stop plugin.
- command - new command to plugin. Command can be entered in message field in format '/plugin <plugin_short_name> <command>'. Command 'help' should show list of supported commands.
- lossless_packet - callback - incoming lossless packet from friend.
- lossy_packet - callback - incoming lossy packet from friend.
- friend_connected - callback - friend became online. Note that it called from friend_connection_status callback so friend is not really connected and ready for sending packets.

Other methods:
- send_lossless - this method sends custom lossless packet. Plugins MUST send lossless packets using this method.
- send_lossy - this method sends custom lossy packet. Plugins MUST send lossy packets using this method.
- load_settings - loads settings stored in default location.
- save_settings - saves settings to default location.
- load_translator - loads translations. Translations must be stored in directory with plugin's data. Files with translations must have the same name as in main app (example: ru_RU.qm).

About import:

Import statement will not work in case you import module that wasn't previously imported by main program and user uses precompiled binary. It's recommended to use importlib module instead: importlib.import_module(module_name)

About GUI:

It's strictly recommended to support both PySide and PyQt4 in GUI. Plugin can have no GUI at all.

Exceptions:

Plugin's methods MUST NOT raise exceptions.

#Examples

You can find examples in [official repo](https://github.com/ingvar1995/toxygen_plugins)

