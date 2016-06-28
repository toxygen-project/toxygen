# How to install Toxygen

## Use precompiled binary:
[Check our releases page](https://github.com/xveduk/toxygen/releases)

## From source code (recommended for developers)

### Windows

1. [Download and install latest Python 3.4](https://www.python.org/downloads/windows/)
2. [Install PySide](https://pypi.python.org/pypi/PySide/1.2.4) (recommended) or [PyQt4](https://riverbankcomputing.com/software/pyqt/download)
3. Install PyAudio: ``pip3 install pyaudio``
4. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
5. Unpack archive  
6. Download latest libtox.dll build, download latest libsodium.a build, put it into \src\libs\
7. Run \src\main.py

[libtox.dll for 32-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip)

[libtox.dll for 64-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86-64_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86-64_shared_release.zip)

[libsodium.a for 32-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip)

[libsodium.a for 64-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86-64_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86-64_static_release.zip)


### Linux

Dependencies:

1. Install latest Python3.4: 
``sudo apt-get install python3``
2. [Install PySide](https://wiki.qt.io/PySide_Binaries_Linux) (recommended) or [PyQt4](https://riverbankcomputing.com/software/pyqt/download)
3. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) with toxav support in your system (install in /usr/lib/)
4. Install PyAudio: 
```bash
sudo apt-get install portaudio19-dev
sudo apt-get install python3-pyaudio
```
Toxygen:

1. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
2. Unpack archive 
3. Run app:
``python3 main.py``

## Compile Toxygen
Check [compile.md](/docs/compile.md) for more info
