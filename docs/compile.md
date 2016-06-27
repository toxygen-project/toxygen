#Compile Toxygen

You can compile Toxygen using [PyInstaller](http://www.pyinstaller.org/)

Install PyInstaller: 
``pip3 install pyinstaller``

``pyinstaller --windowed --icon images/icon.ico main.py``

Don't forget to copy /images/, /sounds/, /translations/, /styles/, /smileys/, /stickers/ to /dist/main/
