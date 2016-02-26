from PySide import QtCore
from notifications import *
from settings import Settings
from profile import Profile
# TODO: add all callbacks (remove test callbacks and use wrappers)
# NOTE: don't forget to call repaint


class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Invoker(QtCore.QObject):

    def event(self, event):
        event.fn(*event.args, **event.kwargs)
        return True

_invoker = Invoker()


def invoke_in_main_thread(fn, *args, **kwargs):
    QtCore.QCoreApplication.postEvent(_invoker, InvokeEvent(fn, *args, **kwargs))


def self_connection_status(st, tox_link):
    """
    :param st: widget on mainscreen which shows status
    :param tox_link: tox instance
    :return: function for tox.callback_self_connection_status
    """
    def wrapped(tox, connection, user_data):
        print 'Connection status: ', str(connection)
        invoke_in_main_thread(st.repaint)
    return wrapped


def friend_status(a, b, c, d):
    print "Friend connected! Friend's data: ", str(a), str(b), str(c)


def friend_message(window):
    """
    :param window: main window
    :return: function for tox.callback_friend_message
    """
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        print 'Message: ', message.decode('utf8')
        if not window.isActiveWindow() and Settings()['notifications']:
            tray_notification('Message', message.decode('utf8'))
        profile = Profile.getInstance()
        invoke_in_main_thread(profile.newMessage, friend_number, message_type, message)
    return wrapped


def init_callbacks(tox, window):
    """
    :param tox: tox instance
    :param window: main window
    """
    tox.callback_friend_status(friend_status, 0)
    tox.callback_friend_message(friend_message(window), 0)
    tox.callback_self_connection_status(self_connection_status(window.connection_status, tox), 0)
