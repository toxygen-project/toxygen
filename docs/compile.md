You can compile Toxygen using [PyInstaller](http://www.pyinstaller.org/)
Install PyInstaller: 
``pip install pyinstaller``

On Linux:

``pyinstaller --windowed main.py``

On Windows:

``pyinstaller --windowed --icon images/icon.ico main.py``

Don't forget to copy /images/, /sounds/, /translations/, /styles/, to /dist/main/