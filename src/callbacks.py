from PySide import QtCore
from notifications import *
from settings import Settings
from profile import Profile
from toxcore_enums_and_consts import *
# TODO: add all callbacks (use wrappers)


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


def self_connection_status(tox_link):
    """
    :param tox_link: tox instance
    :return: function for tox.callback_self_connection_status
    """
    def wrapped(tox, connection, user_data):
        print 'Connection status: ', str(connection)
        profile = Profile.get_instance()
        if profile.status is None:
            status = tox_link.self_get_status()
            invoke_in_main_thread(profile.set_status, status)
        elif connection == TOX_CONNECTION['NONE']:
            invoke_in_main_thread(profile.set_status, None)
    return wrapped


def friend_status(tox, friend_num, new_status, user_data):
    """
    Check friend's status (none, busy, away)
    """
    print "Friend's #{} status changed! New status: {}".format(friend_num, new_status)
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    invoke_in_main_thread(friend.set_status, new_status)


def friend_connection_status(tox, friend_num, new_status, user_data):
    """
    Check friend's connection status (offline, udp, tcp)
    """
    print "Friend #{} connected! Friend's status: {}".format(friend_num, new_status)
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    if new_status == TOX_CONNECTION['NONE']:
        invoke_in_main_thread(friend.set_status, None)
    invoke_in_main_thread(profile.update_filtration)


def friend_name(window):
    """
    :param window: main window
    :return: function for callback friend_name. It updates friend's name
    and calls window repaint
    """
    def wrapped(tox, friend_num, name, size, user_data):
        profile = Profile.get_instance()
        friend = profile.get_friend_by_number(friend_num)
        print 'New name: ', str(friend_num), str(name)
        invoke_in_main_thread(friend.set_name, name)
        if profile.get_active_number() == friend_num:
            invoke_in_main_thread(window.update_active_friend)
    return wrapped


def friend_status_message(window):
    """
    :param window: main window
    :return: function for callback friend_status_message. It updates friend's status message
    and calls window repaint
    """
    def wrapped(tox, friend_num, status_message, size, user_data):
        profile = Profile.get_instance()
        friend = profile.get_friend_by_number(friend_num)
        invoke_in_main_thread(friend.set_status_message, status_message)
        print 'User #{} has new status: {}'.format(friend_num, status_message)
        if profile.get_active_number() == friend_num:
            invoke_in_main_thread(window.update_active_friend)
    return wrapped


def friend_message(window):
    """
    :param window: main window
    :return: function for tox.callback_friend_message. Adds new message to list
    """
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        print 'Message: ', message.decode('utf8')
        profile = Profile.get_instance()
        if not window.isActiveWindow() and Settings()['notifications']:
            friend = profile.get_friend_by_number(friend_number)
            tray_notification(friend.name, message.decode('utf8'))
        invoke_in_main_thread(profile.new_message, friend_number, message_type, message)
    return wrapped


def init_callbacks(tox, window):
    """
    Initialization of all callbacks.
    :param tox: tox instance
    :param window: main window
    """
    tox.callback_friend_status(friend_status, 0)
    tox.callback_friend_message(friend_message(window), 0)
    tox.callback_self_connection_status(self_connection_status(tox), 0)
    tox.callback_friend_connection_status(friend_connection_status, 0)
    tox.callback_friend_name(friend_name(window), 0)
    tox.callback_friend_status_message(friend_status_message(window), 0)
