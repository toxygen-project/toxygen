import pyaudio
import time
import threading
import settings
from toxav_enums import *
import cv2
import itertools
import numpy as np
# TODO: play sound until outgoing call will be started or cancelled and add timeout


class Call:

    def __init__(self, audio=False, video=False):
        self.audio = audio
        self.video = video
        # TODO: add widget for call


class AV:

    def __init__(self, toxav):
        self._toxav = toxav
        self._running = True

        self._calls = {}  # dict: key - friend number, value - Call instance

        self._audio = None
        self._audio_stream = None
        self._audio_thread = None
        self._audio_running = False
        self._out_stream = None

        self._audio_rate = 8000
        self._audio_channels = 1
        self._audio_duration = 60
        self._audio_sample_count = self._audio_rate * self._audio_channels * self._audio_duration // 1000

        self._video = None
        self._video_thread = None
        self._video_running = False

    def stop(self):
        self._running = False
        self.stop_audio_thread()
        self.stop_video_thread()

    def __contains__(self, friend_number):
        return friend_number in self._calls

    # -----------------------------------------------------------------------------------------------------------------
    # Calls
    # -----------------------------------------------------------------------------------------------------------------

    def __call__(self, friend_number, audio, video):
        """Call friend with specified number"""
        self._toxav.call(friend_number, 32 if audio else 0, 5000 if video else 0)
        self._calls[friend_number] = Call(audio, video)
        self.start_audio_thread()
        self.start_video_thread()

    def accept_call(self, friend_number, audio_enabled, video_enabled):

        if self._running:
            self._calls[friend_number] = Call(audio_enabled, video_enabled)
            self._toxav.answer(friend_number, 32 if audio_enabled else 0, 5000 if video_enabled else 0)
            self.start_audio_thread()

    def finish_call(self, friend_number, by_friend=False):

        if not by_friend:
            self._toxav.call_control(friend_number, TOXAV_CALL_CONTROL['CANCEL'])
        if friend_number in self._calls:
            del self._calls[friend_number]
        if not len(self._calls):
            self.stop_audio_thread()

    def toxav_call_state_cb(self, friend_number, state):
        """
        New call state
        """
        pass  # TODO: ignore?
        # if self._running:
        #
        #     if state & TOXAV_FRIEND_CALL_STATE['ACCEPTING_A']:
        #         self._calls[friend_number].audio = True
        #     if state & TOXAV_FRIEND_CALL_STATE['ACCEPTING_V']:
        #         self._calls[friend_number].video = True

    # -----------------------------------------------------------------------------------------------------------------
    # Threads
    # -----------------------------------------------------------------------------------------------------------------

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

    def start_video_thread(self):
        if self._video_thread is not None:
            return

        self._video_running = True

        self._video = cv2.VideoCapture(0)
        self._video.set(cv2.CAP_PROP_FPS, 25)
        self._video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self._video_thread = threading.Thread(target=self.send_video)
        self._video_thread.start()

    def stop_video_thread(self):
        if self._video_thread is None:
            return

        self._video_running = False
        self._video_thread.join()
        self._video_thread = None
        self._video = None

    # -----------------------------------------------------------------------------------------------------------------
    # Incoming chunks
    # -----------------------------------------------------------------------------------------------------------------

    def audio_chunk(self, samples, channels_count, rate):
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

    def video_chunk(self):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # AV sending
    # -----------------------------------------------------------------------------------------------------------------

    def send_audio(self):
        """
        This method sends audio to friends
        """

        while self._audio_running:
            try:
                pcm = self._audio_stream.read(self._audio_sample_count)
                if pcm:
                    for friend_num in self._calls:
                        if self._calls[friend_num].audio:
                            try:
                                self._toxav.audio_send_frame(friend_num, pcm, self._audio_sample_count,
                                                             self._audio_channels, self._audio_rate)
                            except:
                                pass
            except:
                pass

            time.sleep(0.01)

    def send_video(self):
        while self._video_running:
            try:
                result, frame = self._video.read()
                if result:
                    height, width, channels = frame.shape
                    for friend_num in self._calls:
                        if self._calls[friend_num].video:
                            try:  # TODO: bgr => yuv
                                y, u, v = convert_bgr_to_yuv(frame)
                                self._toxav.video_send_frame(friend_num, width, height, y, u, v)
                            except Exception as e:
                                print('1', e)
            except Exception as e:
                print('2', e)

        time.sleep(0.01)


def convert_bgr_to_yuv(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
    y = frame[:480,:].tolist()
    y = list(itertools.chain.from_iterable(y))
    v = np.zeros((240, 320), dtype=np.int)
    v[::2,:] = frame[480:600, :320]
    v[1::2,:] = frame[480:600, 320:]
    v = list(itertools.chain.from_iterable(v))
    u = np.zeros((240, 320), dtype=np.int)
    u[::2,:] = frame[600:, :320]
    u[1::2,:] = frame[600:, 320:]
    u = list(itertools.chain.from_iterable(u))
    return bytes(y), bytes(v), bytes(u)
