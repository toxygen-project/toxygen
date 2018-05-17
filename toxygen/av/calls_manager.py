import threading
import cv2
import av.calls
import utils.ui as util_ui
from messenger.messages import *
import time
from ui import av_widgets


class CallsManager:

    def __init__(self, toxAV, settings):
        self._call = av.calls.AV(toxAV, settings)  # object with data about calls
        self._call_widgets = {}  # dict of incoming call widgets
        self._incoming_calls = set()
        self._settings = settings

    # -----------------------------------------------------------------------------------------------------------------
    # AV support
    # -----------------------------------------------------------------------------------------------------------------

    def get_call(self):
        return self._call

    call = property(get_call)

    def call_click(self, audio=True, video=False):
        """User clicked audio button in main window"""
        num = self.get_active_number()
        if not self.is_active_a_friend():
            return
        if num not in self._call and self.is_active_online():  # start call
            if not self._settings.audio['enabled']:
                return
            self._call(num, audio, video)
            self._screen.active_call()
            if video:
                text = util_ui.tr("Outgoing video call")
            else:
                text = util_ui.tr("Outgoing audio call")
            self.get_curr_friend().append_message(InfoMessage(text, time.time()))
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()
        elif num in self._call:  # finish or cancel call if you call with active friend
            self.stop_call(num, False)

    def incoming_call(self, audio, video, friend_number):
        """
        Incoming call from friend.
        """
        if not self._settings.audio['enabled']:
            return
        friend = self.get_friend_by_number(friend_number)
        if video:
            text = util_ui.tr("Incoming video call")
        else:
            text = util_ui.tr("Incoming audio call")
        friend.append_message(InfoMessage(text, time.time()))
        self._incoming_calls.add(friend_number)
        if friend_number == self.get_active_number():
            self._screen.incoming_call()
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()
        else:
            friend.actions = True
        self._call_widgets[friend_number] = av_widgets.IncomingCallWidget(friend_number, text, friend.name)
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
            text = util_ui.tr("Call declined")
        else:
            text = util_ui.tr("Call finished")
        self._screen.call_finished()
        is_video = self._call.is_video_call(friend_number)
        self._call.finish_call(friend_number, by_friend)  # finish or decline call
        if hasattr(self, '_call_widget'):
            self._call_widget[friend_number].close()
            del self._call_widget[friend_number]

        def destroy_window():
            if is_video:
                cv2.destroyWindow(str(friend_number))

        threading.Timer(2.0, destroy_window).start()
        friend = self.get_friend_by_number(friend_number)
        friend.append_message(InfoMessage(text, time.time()))
        if friend_number == self.get_active_number():
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()

    def friend_exit(self, friend_number):
        if friend_number in self._call:
            self._call.finish_call(friend_number, True)
