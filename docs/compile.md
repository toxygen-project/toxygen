# Compile Toxygen

You can compile Toxygen using [PyInstaller](http://www.pyinstaller.org/)

Install PyInstaller: 
``pip3 install pyinstaller``

Compile Toxygen:
``pyinstaller --windowed --icon images/icon.ico main.py``

Don't forget to copy /images/, /sounds/, /translations/, /styles/, /smileys/, /stickers/, /plugins/ (and /libs/libtox.dll, /libs/libsodium.a on Windows) to /dist/main/
