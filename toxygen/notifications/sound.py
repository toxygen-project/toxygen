import util.util
import wave
import pyaudio
import os.path


SOUND_NOTIFICATION = {
    'MESSAGE': 0,
    'FRIEND_CONNECTION_STATUS': 1,
    'FILE_TRANSFER': 2
}


class AudioFile:
    chunk = 1024

    def __init__(self, fl):
        self.wf = wave.open(fl, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True)

    def play(self):
        data = self.wf.readframes(self.chunk)
        while data:
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        self.stream.close()
        self.p.terminate()


def sound_notification(t):
    """
    Plays sound notification
    :param t: type of notification
    """
    if t == SOUND_NOTIFICATION['MESSAGE']:
        f = get_file_path('message.wav')
    elif t == SOUND_NOTIFICATION['FILE_TRANSFER']:
        f = get_file_path('file.wav')
    else:
        f = get_file_path('contact.wav')
    a = AudioFile(f)
    a.play()
    a.close()


def get_file_path(file_name):
    return os.path.join(util.util.get_sounds_directory(), file_name)
