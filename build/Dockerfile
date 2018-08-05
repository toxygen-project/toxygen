FROM ubuntu:16.04

RUN apt-get update && \
apt-get install build-essential libtool autotools-dev automake checkinstall cmake check git yasm libsodium-dev libopus-dev libvpx-dev pkg-config -y && \
git clone https://github.com/ingvar1995/toxcore.git --branch=ngc_rebase && \
cd toxcore && mkdir _build && cd _build && \
cmake .. && make && make install

RUN apt-get install portaudio19-dev python3-pyqt5 python3-pyaudio python3-pip -y && \
pip3 install --upgrade pip && \
pip3 install numpy pydenticon opencv-python pyinstaller
