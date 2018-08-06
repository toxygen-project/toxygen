#!/usr/bin/env bash

cd ~
git clone https://github.com/toxygen-project/toxygen.git --branch=next_gen
cd toxygen/toxygen

pyinstaller --windowed --icon=images/icon.ico main.py

cp -r styles dist/main/
cp -r plugins dist/main/
mkdir -p dist/main/ui/views
cp -r ui/views dist/main/ui/
cp -r sounds dist/main/
cp -r smileys dist/main/
cp -r stickers dist/main/
cp -r bootstrap dist/main/
cp -r images dist/main/
cp -r translations dist/main/

cd dist
mv main toxygen
cd toxygen
mv main toxygen
wget -O updater https://github.com/toxygen-project/toxygen_updater/releases/download/v0.1/toxygen_updater_linux_64
echo "[Paths]" >> qt.conf
echo "Prefix = PyQt5/Qt" >> qt.conf
cd ..

tar -zcvf toxygen_linux_64.tar.gz toxygen > /dev/null
rm -rf toxygen
