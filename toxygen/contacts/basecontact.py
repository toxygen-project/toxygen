from user_data.settings import *
from PyQt5 import QtCore, QtGui
from wrapper.toxcore_enums_and_consts import TOX_PUBLIC_KEY_SIZE
import utils.util as util
import common.event as event
import contacts.common as common


class BaseContact:
    """
    Class encapsulating TOX contact
    Properties: name (alias of contact or name), status_message, status (connection status)
    widget - widget for update, tox id (or public key)
    Base class for all contacts.
    """

    def __init__(self, profile_manager, name, status_message, widget, tox_id):
        """
        :param name: name, example: 'Toxygen user'
        :param status_message: status message, example: 'Toxing on Toxygen'
        :param widget: ContactItem instance
        :param tox_id: tox id of contact
        """
        self._profile_manager = profile_manager
        self._name, self._status_message = name, status_message
        self._status, self._widget = None, widget
        self._tox_id = tox_id
        self._name_changed_event = event.Event()
        self._status_message_changed_event = event.Event()
        self._status_changed_event = event.Event()
        self._avatar_changed_event = event.Event()
        self.init_widget()

    # -----------------------------------------------------------------------------------------------------------------
    # Name - current name or alias of user
    # -----------------------------------------------------------------------------------------------------------------

    def get_name(self):
        return self._name

    def set_name(self, value):
        if self._name != value:
            self._name = value
            self._widget.name.setText(self._name)
            self._widget.name.repaint()
            self._name_changed_event(self._name)

    name = property(get_name, set_name)

    def get_name_changed_event(self):
        return self._name_changed_event

    name_changed_event = property(get_name_changed_event)

    # -----------------------------------------------------------------------------------------------------------------
    # Status message
    # -----------------------------------------------------------------------------------------------------------------

    def get_status_message(self):
        return self._status_message

    def set_status_message(self, value):
        if self._status_message != value:
            self._status_message = value
            self._widget.status_message.setText(self._status_message)
            self._widget.status_message.repaint()
            self._status_message_changed_event(self._status_message)

    status_message = property(get_status_message, set_status_message)

    def get_status_message_changed_event(self):
        return self._status_message_changed_event

    status_message_changed_event = property(get_status_message_changed_event)

    # -----------------------------------------------------------------------------------------------------------------
    # Status
    # -----------------------------------------------------------------------------------------------------------------

    def get_status(self):
        return self._status

    def set_status(self, value):
        if self._status != value:
            self._status = value
            self._widget.connection_status.update(value)
            self._status_changed_event(self._status)

    status = property(get_status, set_status)

    def get_status_changed_event(self):
        return self._status_changed_event

    status_changed_event = property(get_status_changed_event)

    # -----------------------------------------------------------------------------------------------------------------
    # TOX ID. WARNING: for friend it will return public key, for profile - full address
    # -----------------------------------------------------------------------------------------------------------------

    def get_tox_id(self):
        return self._tox_id

    tox_id = property(get_tox_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars
    # -----------------------------------------------------------------------------------------------------------------

    def load_avatar(self):
        """
        Tries to load avatar of contact or uses default avatar
        """
        avatar_path = self.get_avatar_path()
        width = self._widget.avatar_label.width()
        pixmap = QtGui.QPixmap(avatar_path)
        self._widget.avatar_label.setPixmap(pixmap.scaled(width, width, QtCore.Qt.KeepAspectRatio,
                                                          QtCore.Qt.SmoothTransformation))
        self._widget.avatar_label.repaint()
        self._avatar_changed_event(avatar_path)

    def reset_avatar(self, generate_new):
        avatar_path = self.get_avatar_path()
        if os.path.isfile(avatar_path) and not avatar_path == self._get_default_avatar_path():
            os.remove(avatar_path)
        if generate_new:
            self.set_avatar(common.generate_avatar(self.tox_id))
        else:
            self.load_avatar()

    def set_avatar(self, avatar):
        avatar_path = self.get_contact_avatar_path()
        with open(avatar_path, 'wb') as f:
            f.write(avatar)
        self.load_avatar()

    def get_pixmap(self):
        return self._widget.avatar_label.pixmap()

    def get_avatar_path(self):
        avatar_path = self.get_contact_avatar_path()
        if not os.path.isfile(avatar_path) or not os.path.getsize(avatar_path):  # load default image
            avatar_path = self._get_default_avatar_path()

        return avatar_path

    def get_contact_avatar_path(self):
        directory = util.join_path(self._profile_manager.get_dir(), 'avatars')

        return util.join_path(directory, '{}.png'.format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2]))

    def get_avatar_changed_event(self):
        return self._avatar_changed_event

    avatar_changed_event = property(get_avatar_changed_event)

    # -----------------------------------------------------------------------------------------------------------------
    # Widgets
    # -----------------------------------------------------------------------------------------------------------------

    def init_widget(self):
        self._widget.name.setText(self._name)
        self._widget.status_message.setText(self._status_message)
        self._widget.connection_status.update(self._status)
        self.load_avatar()

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _get_default_avatar_path():
        return util.join_path(util.get_images_directory(), 'avatar.png')
