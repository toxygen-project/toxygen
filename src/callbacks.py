from PySide import QtCore
from notifications import *
from settings import Settings
from profile import Profile
from toxcore_enums_and_consts import *
from toxav_enums import *
from tox import bin_to_string
from ctypes import c_char_p, cast, pointer


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

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - current user
# -----------------------------------------------------------------------------------------------------------------


def self_connection_status(tox_link):
    """
    Current user changed connection status (offline, UDP, TCP)
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


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - friends
# -----------------------------------------------------------------------------------------------------------------


def friend_status(tox, friend_num, new_status, user_data):
    """
    Check friend's status (none, busy, away)
    """
    print "Friend's #{} status changed! New status: {}".format(friend_num, new_status)
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    if friend.status is None and Settings.get_instance()['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
        sound_notification(SOUND_NOTIFICATION['FRIEND_CONNECTION_STATUS'])
    invoke_in_main_thread(friend.set_status, new_status)
    invoke_in_main_thread(profile.update_filtration)


def friend_connection_status(tox, friend_num, new_status, user_data):
    """
    Check friend's connection status (offline, udp, tcp)
    """
    print "Friend #{} connected! Friend's status: {}".format(friend_num, new_status)
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    if new_status == TOX_CONNECTION['NONE']:
        invoke_in_main_thread(profile.friend_exit, friend_num)
        invoke_in_main_thread(profile.update_filtration)
        if Settings.get_instance()['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
            sound_notification(SOUND_NOTIFICATION['FRIEND_CONNECTION_STATUS'])
    elif friend.status is None:
        invoke_in_main_thread(profile.send_avatar, friend_num)


def friend_name(tox, friend_num, name, size, user_data):
    """
    Friend changed his name
    """
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    print 'New name: ', str(friend_num), str(name)
    invoke_in_main_thread(friend.set_name, name)
    if profile.get_active_number() == friend_num:
        invoke_in_main_thread(profile.set_active)


def friend_status_message(tox, friend_num, status_message, size, user_data):
    """
    :return: function for callback friend_status_message. It updates friend's status message
    and calls window repaint
    """
    profile = Profile.get_instance()
    friend = profile.get_friend_by_number(friend_num)
    invoke_in_main_thread(friend.set_status_message, status_message)
    print 'User #{} has new status: {}'.format(friend_num, status_message)
    if profile.get_active_number() == friend_num:
        invoke_in_main_thread(profile.set_active)


def friend_message(window, tray):
    """
    New message from friend
    """
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        profile = Profile.get_instance()
        settings = Settings.get_instance()
        invoke_in_main_thread(profile.new_message, friend_number, message_type, message)
        if not window.isActiveWindow():
            friend = profile.get_friend_by_number(friend_number)
            if settings['notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                invoke_in_main_thread(tray_notification, friend.name, message.decode('utf8'), tray, window)
            if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                sound_notification(SOUND_NOTIFICATION['MESSAGE'])
    return wrapped


def friend_request(tox, public_key, message, message_size, user_data):
    """
    Called when user get new friend request
    """
    print 'Friend request'
    profile = Profile.get_instance()
    key = ''.join(chr(x) for x in public_key[:TOX_PUBLIC_KEY_SIZE])
    tox_id = bin_to_string(key, TOX_PUBLIC_KEY_SIZE)
    if tox_id not in Settings.get_instance()['blocked']:
        invoke_in_main_thread(profile.process_friend_request, tox_id, message.decode('utf-8'))


def friend_typing(tox, friend_number, typing, user_data):
    invoke_in_main_thread(Profile.get_instance().friend_typing, friend_number, typing)

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - file transfers
# -----------------------------------------------------------------------------------------------------------------


def tox_file_recv(window, tray):
    """
    New incoming file
    """
    def wrapped(tox, friend_number, file_number, file_type, size, file_name, file_name_size, user_data):
        profile = Profile.get_instance()
        settings = Settings.get_instance()
        if file_type == TOX_FILE_KIND['DATA']:
            print 'file'
            try:
                file_name = unicode(file_name[:file_name_size].decode('utf-8'))
            except:
                file_name = u'toxygen_file'
            invoke_in_main_thread(profile.incoming_file_transfer,
                                  friend_number,
                                  file_number,
                                  size,
                                  file_name)
            if not window.isActiveWindow():
                friend = profile.get_friend_by_number(friend_number)
                if settings['notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                    invoke_in_main_thread(tray_notification, 'File from ' + friend.name, file_name, tray, window)
                if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                    sound_notification(SOUND_NOTIFICATION['FILE_TRANSFER'])
        else:  # AVATAR
            print 'Avatar'
            invoke_in_main_thread(profile.incoming_avatar,
                                  friend_number,
                                  file_number,
                                  size)
    return wrapped


def file_recv_chunk(tox, friend_number, file_number, position, chunk, length, user_data):
    """
    Incoming chunk
    """
    if not length:
        invoke_in_main_thread(Profile.get_instance().incoming_chunk,
                              friend_number,
                              file_number,
                              position,
                              None)
    else:
        Profile.get_instance().incoming_chunk(friend_number, file_number, position,chunk[:length])


def file_chunk_request(tox, friend_number, file_number, position, size, user_data):
    """
    Outgoing chunk
    """
    if size:
        Profile.get_instance().outgoing_chunk(friend_number, file_number, position, size)
    else:
        invoke_in_main_thread(Profile.get_instance().outgoing_chunk,
                              friend_number,
                              file_number,
                              position,
                              size)


def file_recv_control(tox, friend_number, file_number, file_control, user_data):
    """
    Friend cancelled, paused or resumed file transfer
    """
    if file_control == TOX_FILE_CONTROL['CANCEL']:
        Profile.get_instance().cancel_transfer(friend_number, file_number, True)
    elif file_control == TOX_FILE_CONTROL['PAUSE']:
        Profile.get_instance().pause_transfer(friend_number, file_number, True)
    elif file_control == TOX_FILE_CONTROL['RESUME']:
        Profile.get_instance().resume_transfer(friend_number, file_number, True)


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - audio
# -----------------------------------------------------------------------------------------------------------------

def call_state(toxav, friend_number, mask, user_data):
    """New call state"""
    print friend_number, mask
    if mask == TOXAV_FRIEND_CALL_STATE['FINISHED'] or mask == TOXAV_FRIEND_CALL_STATE['ERROR']:
        invoke_in_main_thread(Profile.get_instance().stop_call, friend_number, True)
    else:
        Profile.get_instance().call.toxav_call_state_cb(friend_number, mask)


def call(toxav, friend_number, audio, video, user_data):
    """Incoming call from friend"""
    print friend_number, audio, video
    invoke_in_main_thread(Profile.get_instance().incoming_call, audio, video, friend_number)


def callback_audio(toxav, friend_number, samples, audio_samples_per_channel, audio_channels_count, rate, user_data):
    """New audio chunk"""
    print audio_samples_per_channel, audio_channels_count, rate
    Profile.get_instance().call.chunk(
        ''.join(chr(x) for x in samples[:audio_samples_per_channel * 2 * audio_channels_count]),
        audio_channels_count,
        rate)


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - initialization
# -----------------------------------------------------------------------------------------------------------------


def init_callbacks(tox, window, tray):
    """
    Initialization of all callbacks.
    :param tox: tox instance
    :param window: main window
    :param tray: tray (for notifications)
    """
    tox.callback_self_connection_status(self_connection_status(tox), 0)

    tox.callback_friend_status(friend_status, 0)
    tox.callback_friend_message(friend_message(window, tray), 0)
    tox.callback_friend_connection_status(friend_connection_status, 0)
    tox.callback_friend_name(friend_name, 0)
    tox.callback_friend_status_message(friend_status_message, 0)
    tox.callback_friend_request(friend_request, 0)
    tox.callback_friend_typing(friend_typing, 0)

    tox.callback_file_recv(tox_file_recv(window, tray), 0)
    tox.callback_file_recv_chunk(file_recv_chunk, 0)
    tox.callback_file_chunk_request(file_chunk_request, 0)
    tox.callback_file_recv_control(file_recv_control, 0)

    toxav = tox.AV
    toxav.callback_call_state(call_state, 0)
    toxav.callback_call(call, 0)
    toxav.callback_audio_receive_frame(callback_audio, 0)

