# How to install Toxygen

## From source code (recommended for developers)

### Windows

1. [Download and install latest Python 2.7](https://www.python.org/downloads/windows/)
2. [Install PySide](https://pypi.python.org/pypi/PySide/1.2.4) *(PyQt4 support will be added later)*
3. Install PyAudio: ``python -m pip install pyaudio``
4. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
5. Unpack archive  
6. Download latest libtox.dll build, download latest libsodium.a build, put it into \src\libs\
7. Run \src\main.py

[libtox.dll for 32-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip)

[libtox.dll for 64-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86-64_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86-64_shared_release.zip)

[libsodium.a for 32-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip)

[libsodium.a for 64-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86-64_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86-64_static_release.zip)


### Linux

- Install Python2.7: 
``sudo apt-get install python2.7``
- [Install PySide](https://wiki.qt.io/PySide_Binaries_Linux) *(PyQt4 support will be added later)*
- Install PyAudio: 
```bash
sudo apt-get install portaudio19-dev
sudo pip install pyaudio
```
- [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
- Unpack archive 
- Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) in your system (install in /usr/lib/)
- Run app:
``python main.py``

## Use precompiled binary:
[Check our releases page](https://github.com/xveduk/toxygen/releases)

## Compile Toxygen
Check [compile.md](/docs/compile.md) for more info
