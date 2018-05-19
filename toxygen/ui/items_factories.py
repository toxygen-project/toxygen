from ui.contact_items import *
from ui.messages_widgets import *


class ContactItemsFactory:

    def __init__(self, settings, main_screen):
        self._settings = settings
        self._friends_list = main_screen.friends_list

    def create_contact_item(self):
        item = ContactItem(self._settings)
        elem = QtWidgets.QListWidgetItem(self._friends_list)
        elem.setSizeHint(QtCore.QSize(250, item.height()))
        self._friends_list.addItem(elem)
        self._friends_list.setItemWidget(elem, item)

        return item


class MessagesItemsFactory:

    def __init__(self, settings, plugin_loader, smiley_loader, main_screen, delete_action):
        self._file_transfers_handler = None
        self._settings, self._plugin_loader = settings, plugin_loader
        self._smiley_loader, self._delete_action = smiley_loader, delete_action
        self._messages = main_screen.messages
        self._message_edit = main_screen.messageEdit

    def set_file_transfers_handler(self, file_transfers_handler):
        self._file_transfers_handler = file_transfers_handler

    def create_message_item(self, message, append=True, pixmap=None):
        item = message.get_widget(self._settings, self._create_message_browser,
                                  self._delete_action, self._messages)
        if pixmap is not None:
            item.set_avatar(pixmap)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

        return item

    def create_inline_item(self, data, append=True, position=0):
        elem = QtWidgets.QListWidgetItem()
        item = InlineImageItem(data, self._messages.width(), elem, self._messages)
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(position, elem)
        self._messages.setItemWidget(elem, item)

        return item

    def create_unsent_file_item(self, message, append=True):
        item = message.get_widget(self._file_transfers_handler, self._settings, self._messages.width(), self._messages)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

        return item

    def create_file_transfer_item(self, message, append=True):
        item = message.get_widget(self._file_transfers_handler, self._settings, self._messages.width(), self._messages)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

        return item

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _create_message_browser(self, text, width, message_type, parent=None):
        return MessageBrowser(self._settings, self._message_edit, self._smiley_loader, self._plugin_loader,
                              text, width, message_type, parent)
