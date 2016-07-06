try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
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
        self.avatar_label = QtGui.QLabel(self)
        self.avatar_label.setGeometry(QtCore.QRect(10, 20, 64, 64))
        self.avatar_label.setScaledContents(False)
        self.name = widgets.DataLabel(self)
        self.name.setGeometry(QtCore.QRect(90, 20, 300, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(True)
        self.name.setFont(font)
        self.call_type = widgets.DataLabel(self)
        self.call_type.setGeometry(QtCore.QRect(90, 55, 300, 25))
        self.call_type.setFont(font)
        self.accept_audio = QtGui.QPushButton(self)
        self.accept_audio.setGeometry(QtCore.QRect(20, 100, 150, 150))
        self.accept_video = QtGui.QPushButton(self)
        self.accept_video.setGeometry(QtCore.QRect(170, 100, 150, 150))
        self.decline = QtGui.QPushButton(self)
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
        pr = profile.Profile.get_instance()
        self.accept_audio.clicked.connect(lambda: pr.accept_call(friend_number, True, False) or self.stop())
        # self.accept_video.clicked.connect(lambda: pr.start_call(friend_number, True, True))
        self.decline.clicked.connect(lambda: pr.stop_call(friend_number, False) or self.stop())

        class SoundPlay(QtCore.QThread):

            def __init__(self):
                QtCore.QThread.__init__(self)

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

    def set_pixmap(self, pixmap):
        self.avatar_label.setPixmap(pixmap)


class AudioMessageRecorder(widgets.CenteredWidget):

    def __init__(self, friend_number, name):
        super(AudioMessageRecorder, self).__init__()
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 20, 250, 20))
        text = QtGui.QApplication.translate("MenuWindow", "Send audio message to friend {}", None, QtGui.QApplication.UnicodeUTF8)
        self.label.setText(text.format(name))
        self.record = QtGui.QPushButton(self)
        self.record.setGeometry(QtCore.QRect(20, 100, 150, 150))

        self.record.setText(QtGui.QApplication.translate("MenuWindow", "Start recording", None,
                                                         QtGui.QApplication.UnicodeUTF8))
        self.record.clicked.connect(self.start_or_stop_recording)
        self.recording = False
        self.friend_num = friend_number

    def start_or_stop_recording(self):
        if not self.recording:
            self.recording = True
            self.record.setText(QtGui.QApplication.translate("MenuWindow", "Stop recording", None,
                                                             QtGui.QApplication.UnicodeUTF8))
        else:
            self.close()


