# How to install Toxygen

## Use precompiled binary:
[Check our releases page](https://github.com/xveduk/toxygen/releases)

##Using pip3

### Windows  (32-bit interpreter)

``pip3.4 install toxygen``
Run app using ``toxygen`` command.

##Linux

1. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) with toxav support in your system (install in /usr/lib/)
2. Install PortAudio: 
``sudo apt-get install portaudio19-dev``
3. Install toxygen: 
``sudo pip3.4 install toxygen``
4 Run toxygen using ``toxygen`` command.

## From source code (recommended for developers)

### Windows

1. [Download and install latest Python 3.4](https://www.python.org/downloads/windows/)
2. [Install PySide](https://pypi.python.org/pypi/PySide/1.2.4) (recommended) or [PyQt4](https://riverbankcomputing.com/software/pyqt/download)
3. Install PyAudio: ``pip3.4 install pyaudio``
4. Install PySocks: ``pip3.4 install PySocks``
5. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
6. Unpack archive  
7. Download latest libtox.dll build, download latest libsodium.a build, put it into \src\libs\
8. Run \src\main.py

[libtox.dll for 32-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip)

[libtox.dll for 64-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86-64_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86-64_shared_release.zip)

[libsodium.a for 32-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip)

[libsodium.a for 64-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86-64_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86-64_static_release.zip)


### Linux

Dependencies:

1. Install latest Python3.4: 
``sudo apt-get install python3``
2. [Install PySide](https://wiki.qt.io/PySide_Binaries_Linux) (recommended), using terminal - ``sudo apt-get install python3-pyside``, or install [PyQt4](https://riverbankcomputing.com/software/pyqt/download).
3. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) with toxav support in your system (install in /usr/lib/)
4. Install PyAudio: 
``sudo apt-get install portaudio19-dev`` and ``sudo apt-get install python3-pyaudio``
5. Install PySocks: ``pip3.4 install PySocks``
6. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
7. Unpack archive 
8. Run app:
``python3.4 main.py``

## Compile Toxygen
Check [compile.md](/docs/compile.md) for more info
