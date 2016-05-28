#Plugins API

In Toxygen plugin is single python module (.py file) and directory with data associated with it. 
Every module must contain one class derived from PluginSuperClass defined in [plugin_super_class.py](/src/plugins/plugin_super_class.py). Instance of this class will be created by PluginLoader class (defined in [plugin_support.py](/src/plugin_support.py) ). This class can enable/disable plugins and send data to it. 

Every plugin has it's own full name and unique short name (1-5 symbols). Main app can get it using special methods. 

All plugin's data should be stored in following structure:

```
/plugins/
|---plugin_short_name.py
|---/plugin_short_name/
	|---settings.json
	|---other_files
```

Plugin can override following methods:
- get_description - this method should return plugin description. 
- get_menu - plugins allowed to add items in friend menu. You can open this menu making right click on friend in friends list. This method should return list of QAction's. Plugin must connect to QAction's triggered() signal. 
- get_window - plugins can have GUI, this method should return window instance or None for plugins without GUI.
- start - plugin was started.
- stop - plugin was stopped.
- command - new command to plugin. Command can be entered in message field in format '/plugin <plugin_short_name> <command>'. Command 'help' should show user list of supported commands.
- lossless_packet - callback - incoming lossless packet from friend.
- lossy_packet - callback - incoming lossy packet from friend.
- friend_connected - callback - friend became online.

Other methods:
- send_lossless - this method send custom lossless packet. Plugins MUST send lossless packets using this method.
- send_lossy - this method send custom lossy packet. Plugins MUST send lossy packets using this method.
- load_settings - loads settings stored in default location.
- save_settings - saves settings to default location.
- load_translator - loads translations. Translations must be stored in directory with plugin's data. Files with translations must have the same name as in main app.


