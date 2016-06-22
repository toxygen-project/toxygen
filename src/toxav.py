from ctypes import c_int, POINTER, c_void_p, byref, ArgumentError, c_uint32, CFUNCTYPE, c_size_t, c_uint8, c_uint16
from ctypes import c_char_p, c_int32, c_bool, cast
from libtox import LibToxAV
from toxav_enums import *


class ToxAV:
    """
    The ToxAV instance type. Each ToxAV instance can be bound to only one Tox instance, and Tox instance can have only
    one ToxAV instance. One must make sure to close ToxAV instance prior closing Tox instance otherwise undefined
    behaviour occurs. Upon closing of ToxAV instance, all active calls will be forcibly terminated without notifying
    peers.
    """

    libtoxav = LibToxAV()

    # -----------------------------------------------------------------------------------------------------------------
    # Creation and destruction
    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self, tox_pointer):
        """
        Start new A/V session. There can only be only one session per Tox instance.

        :param tox_pointer: pointer to Tox instance
        """
        toxav_err_new = c_int()
        ToxAV.libtoxav.toxav_new.restype = POINTER(c_void_p)
        self._toxav_pointer = ToxAV.libtoxav.toxav_new(tox_pointer, byref(toxav_err_new))
        toxav_err_new = toxav_err_new.value
        if toxav_err_new == TOXAV_ERR_NEW['NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif toxav_err_new == TOXAV_ERR_NEW['MALLOC']:
            raise MemoryError('Memory allocation failure while trying to allocate structures required for the A/V '
                              'session.')
        elif toxav_err_new == TOXAV_ERR_NEW['MULTIPLE']:
            raise RuntimeError('Attempted to create a second session for the same Tox instance.')

        self.call_state_cb = None
        self.audio_receive_frame_cb = None
        self.video_receive_frame_cb = None
        self.call_cb = None

    def __del__(self):
        """
        Releases all resources associated with the A/V session.

        If any calls were ongoing, these will be forcibly terminated without notifying peers. After calling this
        function, no other functions may be called and the av pointer becomes invalid.
        """
        ToxAV.libtoxav.toxav_kill(self._toxav_pointer)

    def get_tox_pointer(self):
        """
        Returns the Tox instance the A/V object was created for.

        :return: pointer to the Tox instance
        """
        ToxAV.libtoxav.toxav_get_tox.restype = POINTER(c_void_p)
        return ToxAV.libtoxav.toxav_get_tox(self._toxav_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # A/V event loop
    # -----------------------------------------------------------------------------------------------------------------

    def iteration_interval(self):
        """
        Returns the interval in milliseconds when the next toxav_iterate call should be. If no call is active at the
        moment, this function returns 200.

        :return: interval in milliseconds
        """
        return ToxAV.libtoxav.toxav_iteration_interval(self._toxav_pointer)

    def iterate(self):
        """
        Main loop for the session. This function needs to be called in intervals of toxav_iteration_interval()
        milliseconds. It is best called in the separate thread from tox_iterate.
        """
        ToxAV.libtoxav.toxav_iterate(self._toxav_pointer)

    # -----------------------------------------------------------------------------------------------------------------
    # Call setup
    # -----------------------------------------------------------------------------------------------------------------

    def call(self, friend_number, audio_bit_rate, video_bit_rate):
        """
        Call a friend. This will start ringing the friend.

        It is the client's responsibility to stop ringing after a certain timeout, if such behaviour is desired. If the
        client does not stop ringing, the library will not stop until the friend is disconnected. Audio and video
        receiving are both enabled by default.

        :param friend_number: The friend number of the friend that should be called.
        :param audio_bit_rate: Audio bit rate in Kb/sec. Set this to 0 to disable audio sending.
        :param video_bit_rate: Video bit rate in Kb/sec. Set this to 0 to disable video sending.
        :return: True on success.
        """
        toxav_err_call = c_int()
        result = ToxAV.libtoxav.toxav_call(self._toxav_pointer, c_uint32(friend_number), c_uint32(audio_bit_rate),
                                           c_uint32(video_bit_rate), byref(toxav_err_call))
        toxav_err_call = toxav_err_call.value
        if toxav_err_call == TOXAV_ERR_CALL['OK']:
            return bool(result)
        elif toxav_err_call == TOXAV_ERR_CALL['MALLOC']:
            raise MemoryError('A resource allocation error occurred while trying to create the structures required for '
                              'the call.')
        elif toxav_err_call == TOXAV_ERR_CALL['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_call == TOXAV_ERR_CALL['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend number did not designate a valid friend.')
        elif toxav_err_call == TOXAV_ERR_CALL['FRIEND_NOT_CONNECTED']:
            raise ArgumentError('The friend was valid, but not currently connected.')
        elif toxav_err_call == TOXAV_ERR_CALL['FRIEND_ALREADY_IN_CALL']:
            raise ArgumentError('Attempted to call a friend while already in an audio or video call with them.')
        elif toxav_err_call == TOXAV_ERR_CALL['INVALID_BIT_RATE']:
            raise ArgumentError('Audio or video bit rate is invalid.')

    def callback_call(self, callback, user_data):
        """
        Set the callback for the `call` event. Pass None to unset.

        :param callback: The function for the call callback.

        Should take pointer (c_void_p) to ToxAV object,
        The friend number (c_uint32) from which the call is incoming.
        True (c_bool) if friend is sending audio.
        True (c_bool) if friend is sending video.
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        c_callback = CFUNCTYPE(None, c_void_p, c_uint32, c_bool, c_bool, c_void_p)
        self.call_cb = c_callback(callback)
        ToxAV.libtoxav.toxav_callback_call(self._toxav_pointer, self.call_cb, user_data)

    def answer(self, friend_number, audio_bit_rate, video_bit_rate):
        """
        Accept an incoming call.

        If answering fails for any reason, the call will still be pending and it is possible to try and answer it later.
        Audio and video receiving are both enabled by default.

        :param friend_number: The friend number of the friend that is calling.
        :param audio_bit_rate: Audio bit rate in Kb/sec. Set this to 0 to disable audio sending.
        :param video_bit_rate: Video bit rate in Kb/sec. Set this to 0 to disable video sending.
        :return: True on success.
        """
        toxav_err_answer = c_int()
        result = ToxAV.libtoxav.toxav_answer(self._toxav_pointer, c_uint32(friend_number), c_uint32(audio_bit_rate),
                                             c_uint32(video_bit_rate), byref(toxav_err_answer))
        toxav_err_answer = toxav_err_answer.value
        if toxav_err_answer == TOXAV_ERR_ANSWER['OK']:
            return bool(result)
        elif toxav_err_answer == TOXAV_ERR_ANSWER['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_answer == TOXAV_ERR_ANSWER['CODEC_INITIALIZATION']:
            raise RuntimeError('Failed to initialize codecs for call session. Note that codec initiation will fail if '
                               'there is no receive callback registered for either audio or video.')
        elif toxav_err_answer == TOXAV_ERR_ANSWER['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend number did not designate a valid friend.')
        elif toxav_err_answer == TOXAV_ERR_ANSWER['FRIEND_NOT_CALLING']:
            raise ArgumentError('The friend was valid, but they are not currently trying to initiate a call. This is '
                                'also returned if this client is already in a call with the friend.')
        elif toxav_err_answer == TOXAV_ERR_ANSWER['INVALID_BIT_RATE']:
            raise ArgumentError('Audio or video bit rate is invalid.')

    # -----------------------------------------------------------------------------------------------------------------
    # Call state graph
    # -----------------------------------------------------------------------------------------------------------------

    def callback_call_state(self, callback, user_data):
        """
        Set the callback for the `call_state` event. Pass None to unset.

        :param callback: Python function.
        The function for the call_state callback.

        Should take pointer (c_void_p) to ToxAV object,
        The friend number (c_uint32) for which the call state changed.
        The bitmask of the new call state which is guaranteed to be different than the previous state. The state is set
        to 0 when the call is paused. The bitmask represents all the activities currently performed by the friend.
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        c_callback = CFUNCTYPE(None, c_void_p, c_uint32, c_uint32, c_void_p)
        self.call_state_cb = c_callback(callback)
        ToxAV.libtoxav.toxav_callback_call_state(self._toxav_pointer, self.call_state_cb, user_data)

    # -----------------------------------------------------------------------------------------------------------------
    # Call control
    # -----------------------------------------------------------------------------------------------------------------

    def call_control(self, friend_number, control):
        """
        Sends a call control command to a friend.

        :param friend_number: The friend number of the friend this client is in a call with.
        :param control: The control command to send.
        :return: True on success.
        """
        toxav_err_call_control = c_int()
        result = ToxAV.libtoxav.toxav_call_control(self._toxav_pointer, c_uint32(friend_number), c_int(control),
                                                   byref(toxav_err_call_control))
        toxav_err_call_control = toxav_err_call_control.value
        if toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['OK']:
            return bool(result)
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number passed did not designate a valid friend.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['FRIEND_NOT_IN_CALL']:
            raise RuntimeError('This client is currently not in a call with the friend. Before the call is answered, '
                               'only CANCEL is a valid control.')
        elif toxav_err_call_control == TOXAV_ERR_CALL_CONTROL['INVALID_TRANSITION']:
            raise RuntimeError('Happens if user tried to pause an already paused call or if trying to resume a call '
                               'that is not paused.')

    # -----------------------------------------------------------------------------------------------------------------
    # TODO Controlling bit rates
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # A/V sending
    # -----------------------------------------------------------------------------------------------------------------

    def audio_send_frame(self, friend_number, pcm, sample_count, channels, sampling_rate):
        """
        Send an audio frame to a friend.

        The expected format of the PCM data is: [s1c1][s1c2][...][s2c1][s2c2][...]...
        Meaning: sample 1 for channel 1, sample 1 for channel 2, ...
        For mono audio, this has no meaning, every sample is subsequent. For stereo, this means the expected format is
        LRLRLR... with samples for left and right alternating.

        :param friend_number: The friend number of the friend to which to send an audio frame.
        :param pcm: An array of audio samples. The size of this array must be sample_count * channels.
        :param sample_count: Number of samples in this frame. Valid numbers here are
        ((sample rate) * (audio length) / 1000), where audio length can be 2.5, 5, 10, 20, 40 or 60 milliseconds.
        :param channels: Number of audio channels. Sulpported values are 1 and 2.
        :param sampling_rate: Audio sampling rate used in this frame. Valid sampling rates are 8000, 12000, 16000,
        24000, or 48000.
        """
        toxav_err_send_frame = c_int()
        result = ToxAV.libtoxav.toxav_audio_send_frame(self._toxav_pointer, c_uint32(friend_number),
                                                       cast(pcm, c_void_p),
                                                       c_size_t(sample_count), c_uint8(channels),
                                                       c_uint32(sampling_rate), byref(toxav_err_send_frame))
        toxav_err_send_frame = toxav_err_send_frame.value
        if toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['OK']:
            return bool(result)
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['NULL']:
            raise ArgumentError('The samples data pointer was NULL.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number passed did not designate a valid friend.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['FRIEND_NOT_IN_CALL']:
            raise RuntimeError('This client is currently not in a call with the friend.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['INVALID']:
            raise ArgumentError('One of the frame parameters was invalid. E.g. the resolution may be too small or too '
                                'large, or the audio sampling rate may be unsupported.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['PAYLOAD_TYPE_DISABLED']:
            raise RuntimeError('Either friend turned off audio or video receiving or we turned off sending for the said'
                               'payload.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['RTP_FAILED']:
            RuntimeError('Failed to push frame through rtp interface.')

    def video_send_frame(self, friend_number, width, height, y, u, v):
        """
        Send a video frame to a friend.

        Y - plane should be of size: height * width
        U - plane should be of size: (height/2) * (width/2)
        V - plane should be of size: (height/2) * (width/2)

        :param friend_number: The friend number of the friend to which to send a video frame.
        :param width: Width of the frame in pixels.
        :param height: Height of the frame in pixels.
        :param y: Y (Luminance) plane data.
        :param u: U (Chroma) plane data.
        :param v: V (Chroma) plane data.
        """
        toxav_err_send_frame = c_int()
        result = ToxAV.libtoxav.toxav_video_send_frame(self._toxav_pointer, c_uint32(friend_number), c_uint16(width),
                                                       c_uint16(height), c_char_p(y), c_char_p(u), c_char_p(v),
                                                       byref(toxav_err_send_frame))
        toxav_err_send_frame = toxav_err_send_frame.value
        if toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['OK']:
            return bool(result)
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['NULL']:
            raise ArgumentError('One of Y, U, or V was NULL.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['FRIEND_NOT_FOUND']:
            raise ArgumentError('The friend_number passed did not designate a valid friend.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['FRIEND_NOT_IN_CALL']:
            raise RuntimeError('This client is currently not in a call with the friend.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['SYNC']:
            raise RuntimeError('Synchronization error occurred.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['INVALID']:
            raise ArgumentError('One of the frame parameters was invalid. E.g. the resolution may be too small or too '
                                'large, or the audio sampling rate may be unsupported.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['PAYLOAD_TYPE_DISABLED']:
            raise RuntimeError('Either friend turned off audio or video receiving or we turned off sending for the said'
                               'payload.')
        elif toxav_err_send_frame == TOXAV_ERR_SEND_FRAME['RTP_FAILED']:
            RuntimeError('Failed to push frame through rtp interface.')

    # -----------------------------------------------------------------------------------------------------------------
    # A/V receiving
    # -----------------------------------------------------------------------------------------------------------------

    def callback_audio_receive_frame(self, callback, user_data):
        """
        Set the callback for the `audio_receive_frame` event. Pass None to unset.

        :param callback: Python function.
        Function for the audio_receive_frame callback. The callback can be called multiple times per single
        iteration depending on the amount of queued frames in the buffer. The received format is the same as in send
        function.

        Should take pointer (c_void_p) to ToxAV object,
        The friend number (c_uint32) of the friend who sent an audio frame.
        An array (c_uint8) of audio samples (sample_count * channels elements).
        The number (c_size_t) of audio samples per channel in the PCM array.
        Number (c_uint8) of audio channels.
        Sampling rate (c_uint32) used in this frame.
        pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        c_callback = CFUNCTYPE(None, c_void_p, c_uint32, POINTER(c_uint8), c_size_t, c_uint8, c_uint32, c_void_p)
        self.audio_receive_frame_cb = c_callback(callback)
        ToxAV.libtoxav.toxav_callback_audio_receive_frame(self._toxav_pointer, self.audio_receive_frame_cb, user_data)

    def callback_video_receive_frame(self, callback, user_data):
        """
        Set the callback for the `video_receive_frame` event. Pass None to unset.

        :param callback: Python function.
        The function type for the video_receive_frame callback.

        Should take
        toxAV           pointer (c_void_p) to ToxAV object,
        friend_number   The friend number (c_uint32) of the friend who sent a video frame.
        width           Width (c_uint16) of the frame in pixels.
        height          Height (c_uint16) of the frame in pixels.
        y
        u
        v               Plane data (POINTER(c_uint8)).
                            The size of plane data is derived from width and height where
                            Y = MAX(width, abs(ystride)) * height,
                            U = MAX(width/2, abs(ustride)) * (height/2) and
                            V = MAX(width/2, abs(vstride)) * (height/2).
        ystride
        ustride
        vstride         Strides data (c_int32). Strides represent padding for each plane that may or may not be present. You must
                        handle strides in your image processing code. Strides are negative if the image is bottom-up
                        hence why you MUST abs() it when calculating plane buffer size.
        user_data       pointer (c_void_p) to user_data
        :param user_data: pointer (c_void_p) to user data
        """
        c_callback = CFUNCTYPE(None, c_void_p, c_uint32, c_uint16, c_uint16, POINTER(c_uint8), POINTER(c_uint8),
                               POINTER(c_uint8), c_int32, c_int32, c_int32, c_void_p)
        self.video_receive_frame_cb = c_callback(callback)
        ToxAV.libtoxav.toxav_callback_video_receive_frame(self._toxav_pointer, self.video_receive_frame_cb, user_data)
