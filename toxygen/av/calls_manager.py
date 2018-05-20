import threading
import cv2
import av.calls
from messenger.messages import *
from ui import av_widgets
import common.event as event


class CallsManager:

    def __init__(self, toxAV, settings, screen, contacts_manager):
        self._call = av.calls.AV(toxAV, settings)  # object with data about calls
        self._call_widgets = {}  # dict of incoming call widgets
        self._incoming_calls = set()
        self._settings = settings
        self._screen = screen
        self._contacts_manager = contacts_manager
        self._call_started_event = event.Event()  # friend_number, audio, video, is_outgoing
        self._call_finished_event = event.Event()  # friend_number, is_declined

    def set_toxav(self, toxav):
        self._call.set_toxav(toxav)

    # -----------------------------------------------------------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------------------------------------------------------

    def get_call_started_event(self):
        return self._call_started_event

    call_started_event = property(get_call_started_event)

    def get_call_finished_event(self):
        return self._call_finished_event

    call_finished_event = property(get_call_finished_event)

    # -----------------------------------------------------------------------------------------------------------------
    # AV support
    # -----------------------------------------------------------------------------------------------------------------

    def call_click(self, audio=True, video=False):
        """User clicked audio button in main window"""
        num = self._contacts_manager.get_active_number()
        if not self._contacts_manager.is_active_a_friend():
            return
        if num not in self._call and self._contacts_manager.is_active_online():  # start call
            if not self._settings.audio['enabled']:
                return
            self._call(num, audio, video)
            self._screen.active_call()
            self._call_started_event(num, audio, video, True)
        elif num in self._call:  # finish or cancel call if you call with active friend
            self.stop_call(num, False)

    def incoming_call(self, audio, video, friend_number):
        """
        Incoming call from friend.
        """
        if not self._settings.audio['enabled']:
            return
        friend = self._contacts_manager.get_friend_by_number(friend_number)
        self._call_started_event(friend_number, audio, video, False)
        self._incoming_calls.add(friend_number)
        if friend_number == self._contacts_manager.get_active_number():
            self._screen.incoming_call()
        else:
            friend.actions = True
        text = util_ui.tr("Incoming video call") if video else util_ui.tr("Incoming audio call")
        self._call_widgets[friend_number] = self._get_incoming_call_widget(friend_number, text, friend.name)
        self._call_widgets[friend_number].set_pixmap(friend.get_pixmap())
        self._call_widgets[friend_number].show()

    def accept_call(self, friend_number, audio, video):
        """
        Accept incoming call with audio or video
        """
        self._call.accept_call(friend_number, audio, video)
        self._screen.active_call()
        if friend_number in self._incoming_calls:
            self._incoming_calls.remove(friend_number)
        del self._call_widgets[friend_number]

    def stop_call(self, friend_number, by_friend):
        """
        Stop call with friend
        """
        if friend_number in self._incoming_calls:
            self._incoming_calls.remove(friend_number)
            is_declined = True
        else:
            is_declined = False
        self._screen.call_finished()
        is_video = self._call.is_video_call(friend_number)
        self._call.finish_call(friend_number, by_friend)  # finish or decline call
        if friend_number in self._call_widgets:
            self._call_widgets[friend_number].close()
            del self._call_widgets[friend_number]

        def destroy_window():
            if is_video:
                cv2.destroyWindow(str(friend_number))

        threading.Timer(2.0, destroy_window).start()
        self._call_finished_event(friend_number, is_declined)

    def friend_exit(self, friend_number):
        if friend_number in self._call:
            self._call.finish_call(friend_number, True)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _get_incoming_call_widget(self, friend_number, text, friend_name):
        return av_widgets.IncomingCallWidget(self._settings, self, friend_number, text, friend_name)
