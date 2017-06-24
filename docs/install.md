# How to install Toxygen

## Use precompiled binary (recommended for users):
[Check our releases page](https://github.com/toxygen-project/toxygen/releases)

## Using pip3

### Windows

``pip install toxygen``

Run app using ``toxygen`` command.

### Linux

1. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) with toxav support in your system (install in /usr/lib/)
2. Install PortAudio: 
``sudo apt-get install portaudio19-dev``
3. For 32-bit Linux install PyQt5: ``sudo apt-get install python3-pyqt5``
4. Install [OpenCV](http://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html)
5. Install toxygen: 
``sudo pip3 install toxygen``
6. Run toxygen using ``toxygen`` command.

## Packages

Arch Linux: [AUR](https://aur.archlinux.org/packages/toxygen-git/)

Debian/Ubuntu: [tox.chat](https://tox.chat/download.html#gnulinux)

## From source code (recommended for developers)

### Windows

Note: 32-bit Python isn't supported due to bug with videocalls. It is strictly recommended to use 64-bit Python.

1. [Download and install latest Python 3 64-bit](https://www.python.org/downloads/windows/)
2. Install PyQt5: ``pip install pyqt5``
3. Install PyAudio: ``pip install pyaudio``
4. Download [numpy](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) and [OpenCV](http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv). Install it using ``pip install <file_name>``.
5. [Download toxygen](https://github.com/toxygen-project/toxygen/archive/master.zip)
6. Unpack archive
7. Download latest libtox.dll build, download latest libsodium.a build, put it into \src\libs\
8. Run \toxygen\main.py.

Optional: install toxygen using setup.py: ``python setup.py install``

[libtox.dll for 32-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86_shared_release.zip)

[libtox.dll for 64-bit Python](https://build.tox.chat/view/libtoxcore/job/libtoxcore_build_windows_x86-64_shared_release/lastSuccessfulBuild/artifact/libtoxcore_build_windows_x86-64_shared_release.zip)

[libsodium.a for 32-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86_static_release.zip)

[libsodium.a for 64-bit Python](https://build.tox.chat/view/libsodium/job/libsodium_build_windows_x86-64_static_release/lastSuccessfulBuild/artifact/libsodium_build_windows_x86-64_static_release.zip)

### Linux

1. Install latest Python3: 
``sudo apt-get install python3``
2. Install PyQt5: ``sudo apt-get install python3-pyqt5`` or ``sudo pip3 install pyqt5``
3. Install [toxcore](https://github.com/irungentoo/toxcore/blob/master/INSTALL.md) with toxav support in your system (install in /usr/lib/)
4. Install PyAudio: 
``sudo apt-get install portaudio19-dev`` and ``sudo apt-get install python3-pyaudio`` (or ``sudo pip3 install pyaudio``)
5. Install NumPy: ``sudo pip3 install numpy``
6. Install [OpenCV](http://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html)
7. [Download toxygen](https://github.com/toxygen-project/toxygen/archive/master.zip)
8. Unpack archive
9. Run app:
``python3 main.py``

Optional: install toxygen using setup.py: ``python3 setup.py install``
