try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
import basecontact
from messages import *
from history import *
from settings import ProfileHelper
from toxcore_enums_and_consts import *
from util import curr_directory


class Contact(basecontact.BaseContact):
    """
    Class encapsulating TOX contact
    Properties: name (alias of contact or name), status_message, status (connection status)
    widget - widget for update
    """

    def __init__(self, message_getter, name, status_message, widget, tox_id):
        """
        :param name: name, example: 'Toxygen user'
        :param status_message: status message, example: 'Toxing on Toxygen'
        :param widget: ContactItem instance
        :param tox_id: tox id of contact
        """
        super().__init__(name, status_message, widget, tox_id)
        self._message_getter = message_getter
        self._new_messages = False
        self._visible = True
        self._corr = []
        self._unsaved_messages = 0
        self._history_loaded = self._new_actions = False
        self._curr_text = ''

    def __del__(self):
        self.set_visibility(False)
        del self._widget
        if hasattr(self, '_message_getter'):
            del self._message_getter

    def load_corr(self, first_time=True):
        """
        :param first_time: friend became active, load first part of messages
        """
        if (first_time and self._history_loaded) or (not hasattr(self, '_message_getter')):
            return
        data = list(self._message_getter.get(PAGE_SIZE))
        if data is not None and len(data):
            data.reverse()
        else:
            return
        data = list(map(lambda tupl: TextMessage(*tupl), data))
        self._corr = data + self._corr
        self._history_loaded = True

    def get_corr_for_saving(self):
        """
        Get data to save in db
        :return: list of unsaved messages or []
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        messages = list(filter(lambda x: x.get_type() <= 1, self._corr))
        return list(
            map(lambda x: x.get_data(), list(messages[-self._unsaved_messages:]))) if self._unsaved_messages else []

    def get_corr(self):
        return self._corr[:]

    def append_message(self, message):
        """
        :param message: text or file transfer message
        """
        self._corr.append(message)
        if message.get_type() <= 1:
            self._unsaved_messages += 1

    def get_last_message_text(self):
        messages = list(filter(lambda x: x.get_type() <= 1 and x.get_owner() != MESSAGE_OWNER['FRIEND'], self._corr))
        if messages:
            return messages[-1].get_data()[0]
        else:
            return ''

    def clear_corr(self):
        """
        Clear messages list
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        # don't delete data about active file transfer
        self._corr = list(filter(lambda x: x.get_type() in (2, 3) and (x.get_status() >= 2 or x.get_status() is None),
                                 self._corr))
        self._unsaved_messages = 0

    def delete_old_messages(self):
        old = filter(lambda x: x.get_type() in (2, 3) and (x.get_status() >= 2 or x.get_status() is None),
                     self._corr[:-SAVE_MESSAGES])
        old = list(old)
        l = max(len(self._corr) - SAVE_MESSAGES, 0) - len(old)
        self._unsaved_messages -= l
        self._corr = old + self._corr[-SAVE_MESSAGES:]

    def get_curr_text(self):
        return self._curr_text

    def set_curr_text(self, value):
        self._curr_text = value

    curr_text = property(get_curr_text, set_curr_text)

    # -----------------------------------------------------------------------------------------------------------------
    # Visibility in friends' list
    # -----------------------------------------------------------------------------------------------------------------

    def get_visibility(self):
        return self._visible

    def set_visibility(self, value):
        self._visible = value

    visibility = property(get_visibility, set_visibility)

    # -----------------------------------------------------------------------------------------------------------------
    # Unread messages and actions
    # -----------------------------------------------------------------------------------------------------------------

    def get_actions(self):
        return self._new_actions

    def set_actions(self, value):
        self._new_actions = value
        self._widget.connection_status.update(self.status, value)

    actions = property(get_actions, set_actions)  # unread messages, incoming files, av calls

    def get_messages(self):
        return self._new_messages

    def inc_messages(self):
        self._new_messages += 1
        self._new_actions = True
        self._widget.connection_status.update(self.status, True)
        self._widget.messages.update(self._new_messages)

    def reset_messages(self):
        self._new_actions = False
        self._new_messages = 0
        self._widget.messages.update(self._new_messages)
        self._widget.connection_status.update(self.status, False)

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars
    # -----------------------------------------------------------------------------------------------------------------

    def load_avatar(self):
        """
        Tries to load avatar of contact or uses default avatar
        """
        avatar_path = '{}.png'.format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        os.chdir(ProfileHelper.get_path() + 'avatars/')
        if not os.path.isfile(avatar_path):  # load default image
            avatar_path = 'avatar.png'
            os.chdir(curr_directory() + '/images/')
        width = self._widget.avatar_label.width()
        pixmap = QtGui.QPixmap(QtCore.QSize(width, width))
        pixmap.load(avatar_path)
        self._widget.avatar_label.setScaledContents(False)
        self._widget.avatar_label.setPixmap(pixmap.scaled(width, width, QtCore.Qt.KeepAspectRatio))
        self._widget.avatar_label.repaint()

    def reset_avatar(self):
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        if os.path.isfile(avatar_path):
            os.remove(avatar_path)
            self.load_avatar()

    def set_avatar(self, avatar):
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        with open(avatar_path, 'wb') as f:
            f.write(avatar)
        self.load_avatar()

    def get_pixmap(self):
        return self._widget.avatar_label.pixmap()

    messages = property(get_messages)

