from PyQt5 import QtWidgets, QtCore
from list_items import *


class ItemsFactory:

    def __init__(self, friends_list, messages):
        self._friends = friends_list
        self._messages = messages

    def friend_item(self):
        item = ContactItem()
        elem = QtWidgets.QListWidgetItem(self._friends)
        elem.setSizeHint(QtCore.QSize(250, item.height()))
        self._friends.addItem(elem)
        self._friends.setItemWidget(elem, item)
        return item

    def message_item(self, text, time, name, sent, message_type, append, pixmap):
        item = MessageItem(text, time, name, sent, message_type, self._messages)
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

    def inline_item(self, data, append):
        elem = QtWidgets.QListWidgetItem()
        item = InlineImageItem(data, self._messages.width(), elem)
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)
        return item

    def unsent_file_item(self, file_name, size, name, time, append):
        item = UnsentFileItem(file_name,
                              size,
                              name,
                              time,
                              self._messages.width())
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)
        return item

    def file_transfer_item(self, data, append):
        data.append(self._messages.width())
        item = FileTransferItem(*data)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)
        return item
