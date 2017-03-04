#Plugins

Toxygen is the first [Tox](https://tox.chat/) client with plugins support. Plugin is Python 3.4 module (.py file) and directory with plugin's data which provide some additional functionality. 

#How to write plugin

Check [Plugin API](/docs/plugin_api.md) for more info

#How to install plugin

Toxygen comes without preinstalled plugins.

1. Put plugin and directory with its data into /src/plugins/ or import it via GUI (In menu: Plugins -> Import plugin)
2. Restart Toxygen

##Note: /src/plugins/ should contain plugin_super_class.py and __init__.py

#Plugins list

WARNING: It is unsecure to install plugin not from this list!

[Main repo](https://github.com/toxygen-project/toxygen_plugins)