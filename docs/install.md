# How to install Toxygen

## From source code (recommended for developers)

### Windows

1. [Download and install latest Python 2.7](https://www.python.org/downloads/windows/)
2. [Install PySide](https://pypi.python.org/pypi/PySide/1.2.4) *(PyQt4 support will be added later)*
3. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
4. Unpack archive  
5. Download latest [libtox.dll](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip) build, download latest [libsodium.a](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip) build, put it into \src\libs\
6. Run \src\main.py


### Linux

1. [Install PySide](https://wiki.qt.io/PySide_Binaries_Linux) *(PyQt4 support will be added later)*
2. [Download toxygen](https://github.com/xveduk/toxygen/archive/master.zip)
3. Unpack archive 
4. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) in your system
5. Run app:
``python main.py``

## Use precompiled binary:
[Check our releases page](https://github.com/xveduk/toxygen/releases)

## Compile Toxygen
You can compile Toxygen using [PyInstaller](http://www.pyinstaller.org/):

On Linux:

``pyinstaller --windowed src/main.py``

On Windows:

``pyinstaller --windowed --icon images/icon.ico main.py``

Don't forget to copy /images/, /sounds/, /translations/, /styles/, to /dist/main/
