from PyQt5 import QtCore, QtGui, QtWidgets
import widgets
import profile
import util
import pyaudio
import wave
import settings
from util import curr_directory


class IncomingCallWidget(widgets.CenteredWidget):

    def __init__(self, friend_number, text, name):
        super(IncomingCallWidget, self).__init__()
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(QtCore.QSize(500, 270))
        self.avatar_label = QtWidgets.QLabel(self)
        self.avatar_label.setGeometry(QtCore.QRect(10, 20, 64, 64))
        self.avatar_label.setScaledContents(False)
        self.name = widgets.DataLabel(self)
        self.name.setGeometry(QtCore.QRect(90, 20, 300, 25))
        self._friend_number = friend_number
        font = QtGui.QFont()
        font.setFamily(settings.Settings.get_instance()['font'])
        font.setPointSize(16)
        font.setBold(True)
        self.name.setFont(font)
        self.call_type = widgets.DataLabel(self)
        self.call_type.setGeometry(QtCore.QRect(90, 55, 300, 25))
        self.call_type.setFont(font)
        self.accept_audio = QtWidgets.QPushButton(self)
        self.accept_audio.setGeometry(QtCore.QRect(20, 100, 150, 150))
        self.accept_video = QtWidgets.QPushButton(self)
        self.accept_video.setGeometry(QtCore.QRect(170, 100, 150, 150))
        self.decline = QtWidgets.QPushButton(self)
        self.decline.setGeometry(QtCore.QRect(320, 100, 150, 150))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/accept_audio.png')
        icon = QtGui.QIcon(pixmap)
        self.accept_audio.setIcon(icon)
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/accept_video.png')
        icon = QtGui.QIcon(pixmap)
        self.accept_video.setIcon(icon)
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/decline_call.png')
        icon = QtGui.QIcon(pixmap)
        self.decline.setIcon(icon)
        self.accept_audio.setIconSize(QtCore.QSize(150, 150))
        self.accept_video.setIconSize(QtCore.QSize(140, 140))
        self.decline.setIconSize(QtCore.QSize(140, 140))
        self.accept_audio.setStyleSheet("QPushButton { border: none }")
        self.accept_video.setStyleSheet("QPushButton { border: none }")
        self.decline.setStyleSheet("QPushButton { border: none }")
        self.setWindowTitle(text)
        self.name.setText(name)
        self.call_type.setText(text)
        self._processing = False
        self.accept_audio.clicked.connect(self.accept_call_with_audio)
        self.accept_video.clicked.connect(self.accept_call_with_video)
        self.decline.clicked.connect(self.decline_call)

        class SoundPlay(QtCore.QThread):

            def __init__(self):
                QtCore.QThread.__init__(self)
                self.a = None

            def run(self):
                class AudioFile:
                    chunk = 1024

                    def __init__(self, fl):
                        self.stop = False
                        self.fl = fl
                        self.wf = wave.open(self.fl, 'rb')
                        self.p = pyaudio.PyAudio()
                        self.stream = self.p.open(
                            format=self.p.get_format_from_width(self.wf.getsampwidth()),
                            channels=self.wf.getnchannels(),
                            rate=self.wf.getframerate(),
                            output=True)

                    def play(self):
                        while not self.stop:
                            data = self.wf.readframes(self.chunk)
                            while data and not self.stop:
                                self.stream.write(data)
                                data = self.wf.readframes(self.chunk)
                            self.wf = wave.open(self.fl, 'rb')

                    def close(self):
                        self.stream.close()
                        self.p.terminate()

                self.a = AudioFile(curr_directory() + '/sounds/call.wav')
                self.a.play()
                self.a.close()

        if settings.Settings.get_instance()['calls_sound']:
            self.thread = SoundPlay()
            self.thread.start()
        else:
            self.thread = None

    def stop(self):
        if self.thread is not None:
            self.thread.a.stop = True
            self.thread.wait()
        self.close()

    def accept_call_with_audio(self):
        if self._processing:
            return
        self._processing = True
        pr = profile.Profile.get_instance()
        pr.accept_call(self._friend_number, True, False)
        self.stop()

    def accept_call_with_video(self):
        if self._processing:
            return
        self._processing = True
        pr = profile.Profile.get_instance()
        pr.accept_call(self._friend_number, True, True)
        self.stop()

    def decline_call(self):
        if self._processing:
            return
        self._processing = True
        pr = profile.Profile.get_instance()
        pr.stop_call(self._friend_number, False)
        self.stop()

    def set_pixmap(self, pixmap):
        self.avatar_label.setPixmap(pixmap)
