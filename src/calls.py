import pyaudio
import time
import threading
import settings
from toxav_enums import *
# TODO: play sound until outgoing call will be started or cancelled and add timeout
# TODO: add widget for call

CALL_TYPE = {
    'NONE': 0,
    'AUDIO': 1,
    'VIDEO': 2
}


class AV:

    def __init__(self, toxav):
        self._toxav = toxav
        self._running = True

        self._calls = {}  # dict: key - friend number, value - call type

        self._audio = None
        self._audio_stream = None
        self._audio_thread = None
        self._audio_running = False
        self._out_stream = None

        self._audio_rate = 8000
        self._audio_channels = 1
        self._audio_duration = 60
        self._audio_sample_count = self._audio_rate * self._audio_channels * self._audio_duration // 1000

    def __contains__(self, friend_number):
        return friend_number in self._calls

    def __call__(self, friend_number, audio, video):
        """Call friend with specified number"""
        self._toxav.call(friend_number, 32 if audio else 0, 5000 if video else 0)
        self._calls[friend_number] = CALL_TYPE['AUDIO']
        self.start_audio_thread()

    def finish_call(self, friend_number, by_friend=False):

        if not by_friend:
            self._toxav.call_control(friend_number, TOXAV_CALL_CONTROL['CANCEL'])
        if friend_number in self._calls:
            del self._calls[friend_number]
        if not len(self._calls):
            self.stop_audio_thread()

    def stop(self):
        self._running = False
        self.stop_audio_thread()

    def start_audio_thread(self):
        """
        Start audio sending
        """
        if self._audio_thread is not None:
            return

        self._audio_running = True

        self._audio = pyaudio.PyAudio()
        self._audio_stream = self._audio.open(format=pyaudio.paInt16,
                                              rate=self._audio_rate,
                                              channels=self._audio_channels,
                                              input=True,
                                              input_device_index=settings.Settings.get_instance().audio['input'],
                                              frames_per_buffer=self._audio_sample_count * 10)

        self._audio_thread = threading.Thread(target=self.send_audio)
        self._audio_thread.start()

    def stop_audio_thread(self):

        if self._audio_thread is None:
            return

        self._audio_running = False

        self._audio_thread.join()

        self._audio_thread = None
        self._audio_stream = None
        self._audio = None

        if self._out_stream is not None:
            self._out_stream.stop_stream()
            self._out_stream.close()
            self._out_stream = None

    def chunk(self, samples, channels_count, rate):
        """
        Incoming chunk
        """

        if self._out_stream is None:
            self._out_stream = self._audio.open(format=pyaudio.paInt16,
                                                channels=channels_count,
                                                rate=rate,
                                                output_device_index=settings.Settings.get_instance().audio['output'],
                                                output=True)
        self._out_stream.write(samples)

    def send_audio(self):
        """
        This method sends audio to friends
        """

        while self._audio_running:
            try:
                pcm = self._audio_stream.read(self._audio_sample_count)
                if pcm:
                    for friend in self._calls:
                        if self._calls[friend] & 1:
                            try:
                                self._toxav.audio_send_frame(friend, pcm, self._audio_sample_count,
                                                             self._audio_channels, self._audio_rate)
                            except:
                                pass
            except:
                pass

            time.sleep(0.01)

    def accept_call(self, friend_number, audio_enabled, video_enabled):

        if self._running:
            self._calls[friend_number] = int(video_enabled) * 2 + int(audio_enabled)
            self._toxav.answer(friend_number, 32 if audio_enabled else 0, 5000 if video_enabled else 0)
            self.start_audio_thread()

    def toxav_call_state_cb(self, friend_number, state):
        """
        New call state
        """
        if self._running:

            if state & TOXAV_FRIEND_CALL_STATE['ACCEPTING_A']:
                self._calls[friend_number] |= 1

