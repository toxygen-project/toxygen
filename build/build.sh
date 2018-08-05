#!/usr/bin/env bash
git clone https://github.com/toxygen-project/toxygen.git --branch=next_gen
cd toxygen/toxygen
ln -sf /usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/ /usr/bin/
pyinstaller --windowed --icon=images/icon.ico --hidden-import=PyQt5.uic.plugins main.py
cp -r styles dist/main/
cp -r plugins dist/main/
cp -r sounds dist/main/
cp -r smileys dist/main/
cp -r stickers dist/main/
cp -r bootstrap dist/main/
cp -r images dist/main/
cd dist
mv main toxygen
cd toxygen
mv main toxygen
cd ..
tar -zcvf toxygen_linux_64.tar.gz toxygen
rm -rf toxygen
