from PyQt5 import QtGui
from user_data.settings import Settings
from contacts.profile import Profile
from wrapper.toxcore_enums_and_consts import *
from wrapper.toxav_enums import *
from wrapper.tox import bin_to_string
from plugin_support.plugin_support import PluginLoader
import cv2
import numpy as np
from middleware.threads import invoke_in_main_thread, execute

# TODO: use closures

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - current user
# -----------------------------------------------------------------------------------------------------------------


def self_connection_status(tox, profile):
    """
    Current user changed connection status (offline, UDP, TCP)
    """
    def wrapped(tox_link, connection, user_data):
        print('Connection status: ', str(connection))
        if profile.status is None:
            status = tox.self_get_status()
            invoke_in_main_thread(profile.set_status, status)
        elif connection == TOX_CONNECTION['NONE']:
            invoke_in_main_thread(profile.set_status, None)

    return wrapped


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - friends
# -----------------------------------------------------------------------------------------------------------------


def friend_status(profile, settings):
    def wrapped(tox, friend_num, new_status, user_data):
        """
        Check friend's status (none, busy, away)
        """
        print("Friend's #{} status changed!".format(friend_num))
        friend = profile.get_friend_by_number(friend_num)
        if friend.status is None and settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
            sound_notification(SOUND_NOTIFICATION['FRIEND_CONNECTION_STATUS'])
        invoke_in_main_thread(friend.set_status, new_status)
        invoke_in_main_thread(QtCore.QTimer.singleShot, 5000, lambda: profile.send_files(friend_num))
        invoke_in_main_thread(profile.update_filtration)

    return wrapped


def friend_connection_status(profile, settings, plugin_loader):
    def wrapped(tox, friend_num, new_status, user_data):
        """
        Check friend's connection status (offline, udp, tcp)
        """
        print("Friend #{} connection status: {}".format(friend_num, new_status))
        friend = profile.get_friend_by_number(friend_num)
        if new_status == TOX_CONNECTION['NONE']:
            invoke_in_main_thread(profile.friend_exit, friend_num)
            invoke_in_main_thread(profile.update_filtration)
            if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                sound_notification(SOUND_NOTIFICATION['FRIEND_CONNECTION_STATUS'])
        elif friend.status is None:
            invoke_in_main_thread(profile.send_avatar, friend_num)
            invoke_in_main_thread(plugin_loader.friend_online, friend_num)

    return wrapped


def friend_name(profile):
    def wrapped(tox, friend_num, name, size, user_data):
        """
        Friend changed his name
        """
        print('New name friend #' + str(friend_num))
        invoke_in_main_thread(profile.new_name, friend_num, name)

    return wrapped


def friend_status_message(profile):
    def wrapped(tox, friend_num, status_message, size, user_data):
        """
        :return: function for callback friend_status_message. It updates friend's status message
        and calls window repaint
        """
        friend = profile.get_friend_by_number(friend_num)
        invoke_in_main_thread(friend.set_status_message, status_message)
        print('User #{} has new status'.format(friend_num))
        invoke_in_main_thread(profile.send_messages, friend_num)
        if profile.get_active_number() == friend_num:
            invoke_in_main_thread(profile.set_active)

    return wrapped


def friend_message(profile, settings, window, tray):
    def wrapped(tox, friend_number, message_type, message, size, user_data):
        """
        New message from friend
        """
        message = str(message, 'utf-8')
        invoke_in_main_thread(profile.new_message, friend_number, message_type, message)
        if not window.isActiveWindow():
            friend = profile.get_friend_by_number(friend_number)
            if settings['notifications'] and profile.status != TOX_USER_STATUS['BUSY'] and not settings.locked:
                invoke_in_main_thread(tray_notification, friend.name, message, tray, window)
            if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                sound_notification(SOUND_NOTIFICATION['MESSAGE'])
            invoke_in_main_thread(tray.setIcon, QtGui.QIcon(curr_directory() + '/images/icon_new_messages.png'))

    return wrapped


def friend_request(contacts_manager):
    def wrapped(tox, public_key, message, message_size, user_data):
        """
        Called when user get new friend request
        """
        print('Friend request')
        key = ''.join(chr(x) for x in public_key[:TOX_PUBLIC_KEY_SIZE])
        tox_id = bin_to_string(key, TOX_PUBLIC_KEY_SIZE)
        invoke_in_main_thread(contacts_manager.process_friend_request, tox_id, str(message, 'utf-8'))

    return wrapped


def friend_typing(contacts_manager):
    def wrapped(tox, friend_number, typing, user_data):
        invoke_in_main_thread(contacts_manager.friend_typing, friend_number, typing)

    return wrapped


def friend_read_receipt(contacts_manager):
    def wrapped(tox, friend_number, message_id, user_data):
        contacts_manager.get_friend_by_number(friend_number).dec_receipt()
        if friend_number == contacts_manager.get_active_number():
            invoke_in_main_thread(contacts_manager.receipt)

    return wrapped


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - file transfers
# -----------------------------------------------------------------------------------------------------------------


def tox_file_recv(window, tray, profile, file_transfer_handler, contacts_manager, settings):
    """
    New incoming file
    """
    def wrapped(tox, friend_number, file_number, file_type, size, file_name, file_name_size, user_data):
        if file_type == TOX_FILE_KIND['DATA']:
            print('File')
            try:
                file_name = str(file_name[:file_name_size], 'utf-8')
            except:
                file_name = 'toxygen_file'
            invoke_in_main_thread(file_transfer_handler.incoming_file_transfer,
                                  friend_number,
                                  file_number,
                                  size,
                                  file_name)
            if not window.isActiveWindow():
                friend = contacts_manager.get_friend_by_number(friend_number)
                if settings['notifications'] and profile.status != TOX_USER_STATUS['BUSY'] and not settings.locked:
                    file_from = QtWidgets.QApplication.translate("Callback", "File from")
                    invoke_in_main_thread(tray_notification, file_from + ' ' + friend.name, file_name, tray, window)
                if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
                    sound_notification(SOUND_NOTIFICATION['FILE_TRANSFER'])
                invoke_in_main_thread(tray.setIcon, QtGui.QIcon(curr_directory() + '/images/icon_new_messages.png'))
        else:  # AVATAR
            print('Avatar')
            invoke_in_main_thread(file_transfer_handler.incoming_avatar,
                                  friend_number,
                                  file_number,
                                  size)
    return wrapped


def file_recv_chunk(file_transfer_handler):
    """
    Incoming chunk
    """
    def wrapped(tox, friend_number, file_number, position, chunk, length, user_data):
        execute(file_transfer_handler.incoming_chunk, friend_number, file_number, position,
                chunk[:length] if length else None)

    return wrapped


def file_chunk_request(file_transfer_handler):
    """
    Outgoing chunk
    """
    def wrapped(tox, friend_number, file_number, position, size, user_data):
        execute(file_transfer_handler.outgoing_chunk, friend_number, file_number, position, size)

    return wrapped


def file_recv_control(file_transfer_handler):
    """
    Friend cancelled, paused or resumed file transfer
    """
    def wrapped(tox, friend_number, file_number, file_control, user_data):
        if file_control == TOX_FILE_CONTROL['CANCEL']:
            file_transfer_handler.cancel_transfer(friend_number, file_number, True)
        elif file_control == TOX_FILE_CONTROL['PAUSE']:
            file_transfer_handler.pause_transfer(friend_number, file_number, True)
        elif file_control == TOX_FILE_CONTROL['RESUME']:
            file_transfer_handler.resume_transfer(friend_number, file_number, True)

    return wrapped

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - custom packets
# -----------------------------------------------------------------------------------------------------------------


def lossless_packet(plugin_loader):
    def wrapped(tox, friend_number, data, length, user_data):
        """
        Incoming lossless packet
        """
        data = data[:length]
        invoke_in_main_thread(plugin_loader.callback_lossless, friend_number, data)

    return wrapped


def lossy_packet(plugin_loader):
    def wrapped(tox, friend_number, data, length, user_data):
        """
        Incoming lossy packet
        """
        data = data[:length]
        plugin = PluginLoader.get_instance()
        invoke_in_main_thread(plugin.callback_lossy, friend_number, data)

    return wrapped


# -----------------------------------------------------------------------------------------------------------------
# Callbacks - audio
# -----------------------------------------------------------------------------------------------------------------

def call_state(calls_manager):
    def wrapped(toxav, friend_number, mask, user_data):
        """
        New call state
        """
        print(friend_number, mask)
        if mask == TOXAV_FRIEND_CALL_STATE['FINISHED'] or mask == TOXAV_FRIEND_CALL_STATE['ERROR']:
            invoke_in_main_thread(calls_manager.stop_call, friend_number, True)
        else:
            calls_manager.toxav_call_state_cb(friend_number, mask)

    return wrapped


def call(calls_manager):
    def wrapped(toxav, friend_number, audio, video, user_data):
        """
        Incoming call from friend
        """
        print(friend_number, audio, video)
        invoke_in_main_thread(calls_manager.incoming_call, audio, video, friend_number)

    return wrapped


def callback_audio(calls_manager):
    def wrapped(toxav, friend_number, samples, audio_samples_per_channel, audio_channels_count, rate, user_data):
        """
        New audio chunk
        """
        calls_manager.call.audio_chunk(
            bytes(samples[:audio_samples_per_channel * 2 * audio_channels_count]),
            audio_channels_count,
            rate)

    return wrapped

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - video
# -----------------------------------------------------------------------------------------------------------------


def video_receive_frame(toxav, friend_number, width, height, y, u, v, ystride, ustride, vstride, user_data):
    """
    Creates yuv frame from y, u, v and shows it using OpenCV
    For yuv => bgr we need this YUV420 frame:

              width
    -------------------------
    |                       |
    |          Y            |      height
    |                       |
    -------------------------
    |           |           |
    |  U even   |   U odd   |      height // 4
    |           |           |
    -------------------------
    |           |           |
    |  V even   |   V odd   |      height // 4
    |           |           |
    -------------------------

     width // 2   width // 2

    It can be created from initial y, u, v using slices
    """
    try:
        y_size = abs(max(width, abs(ystride)))
        u_size = abs(max(width // 2, abs(ustride)))
        v_size = abs(max(width // 2, abs(vstride)))

        y = np.asarray(y[:y_size * height], dtype=np.uint8).reshape(height, y_size)
        u = np.asarray(u[:u_size * height // 2], dtype=np.uint8).reshape(height // 2, u_size)
        v = np.asarray(v[:v_size * height // 2], dtype=np.uint8).reshape(height // 2, v_size)

        width -= width % 4
        height -= height % 4

        frame = np.zeros((int(height * 1.5), width), dtype=np.uint8)

        frame[:height, :] = y[:height, :width]
        frame[height:height * 5 // 4, :width // 2] = u[:height // 2:2, :width // 2]
        frame[height:height * 5 // 4, width // 2:] = u[1:height // 2:2, :width // 2]

        frame[height * 5 // 4:, :width // 2] = v[:height // 2:2, :width // 2]
        frame[height * 5 // 4:, width // 2:] = v[1:height // 2:2, :width // 2]

        frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)

        invoke_in_main_thread(cv2.imshow, str(friend_number), frame)
    except Exception as ex:
        print(ex)

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - groups
# -----------------------------------------------------------------------------------------------------------------


def show_gc_notification(window, tray, message, group_number, peer_number):
    profile = Profile.get_instance()
    settings = Settings.get_instance()
    chat = profile.get_group_by_number(group_number)
    peer_name = chat.get_peer_name(peer_number)
    if not window.isActiveWindow() and (profile.name in message or settings['group_notifications']):
        if settings['notifications'] and profile.status != TOX_USER_STATUS['BUSY'] and not settings.locked:
            invoke_in_main_thread(tray_notification, chat.name + ' ' + peer_name, message, tray, window)
        if settings['sound_notifications'] and profile.status != TOX_USER_STATUS['BUSY']:
            sound_notification(SOUND_NOTIFICATION['MESSAGE'])
        invoke_in_main_thread(tray.setIcon, QtGui.QIcon(curr_directory() + '/images/icon_new_messages.png'))

# -----------------------------------------------------------------------------------------------------------------
# Callbacks - initialization
# -----------------------------------------------------------------------------------------------------------------


def init_callbacks(tox, profile, settings, plugin_loader, contacts_manager,
                   calls_manager, file_transfer_handler, window, tray):
    """
    Initialization of all callbacks.
    :param tox: tox instance
    :param window: main window
    :param tray: tray (for notifications)
    """
    tox.callback_self_connection_status(self_connection_status(tox, profile), 0)

    tox.callback_friend_status(friend_status(profile, settings), 0)
    tox.callback_friend_message(friend_message(profile, settings, window, tray), 0)
    tox.callback_friend_connection_status(friend_connection_status(profile, settings, plugin_loader), 0)
    tox.callback_friend_name(friend_name(profile), 0)
    tox.callback_friend_status_message(friend_status_message(profile), 0)
    tox.callback_friend_request(friend_request(contacts_manager), 0)
    tox.callback_friend_typing(friend_typing(contacts_manager), 0)
    tox.callback_friend_read_receipt(friend_read_receipt(contacts_manager), 0)

    tox.callback_file_recv(tox_file_recv(window, tray, profile, file_transfer_handler, contacts_manager, settings), 0)
    tox.callback_file_recv_chunk(file_recv_chunk(file_transfer_handler), 0)
    tox.callback_file_chunk_request(file_chunk_request(file_transfer_handler), 0)
    tox.callback_file_recv_control(file_recv_control(file_transfer_handler), 0)

    toxav.callback_call_state(call_state(calls_manager), 0)
    toxav.callback_call(call(calls_manager), 0)
    toxav.callback_audio_receive_frame(callback_audio(calls_manager), 0)
    toxav.callback_video_receive_frame(video_receive_frame, 0)

    tox.callback_friend_lossless_packet(lossless_packet(plugin_loader), 0)
    tox.callback_friend_lossy_packet(lossy_packet(plugin_loader), 0)

