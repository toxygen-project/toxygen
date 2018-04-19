

class Call:

    def __init__(self, out_audio, out_video, in_audio=False, in_video=False):
        self._in_audio = in_audio
        self._in_video = in_video
        self._out_audio = out_audio
        self._out_video = out_video
        self._is_active = False

    def get_is_active(self):
        return self._is_active

    def set_is_active(self, value):
        self._is_active = value

    is_active = property(get_is_active, set_is_active)

    # -----------------------------------------------------------------------------------------------------------------
    # Audio
    # -----------------------------------------------------------------------------------------------------------------

    def get_in_audio(self):
        return self._in_audio

    def set_in_audio(self, value):
        self._in_audio = value

    in_audio = property(get_in_audio, set_in_audio)

    def get_out_audio(self):
        return self._out_audio

    def set_out_audio(self, value):
        self._out_audio = value

    out_audio = property(get_out_audio, set_out_audio)

    # -----------------------------------------------------------------------------------------------------------------
    # Video
    # -----------------------------------------------------------------------------------------------------------------

    def get_in_video(self):
        return self._in_video

    def set_in_video(self, value):
        self._in_video = value

    in_video = property(get_in_video, set_in_video)

    def get_out_video(self):
        return self._out_video

    def set_out_video(self, value):
        self._out_video = value

    out_video = property(get_out_video, set_out_video)
