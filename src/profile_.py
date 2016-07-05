from list_items import *
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from friend import *
from settings import *
from toxcore_enums_and_consts import *
from ctypes import *
from util import log, Singleton, curr_directory
from tox_dns import tox_dns
from history import *
from file_transfers import *
import time
import calls
import avwidgets
import plugin_support


class Profile(contact.Contact, Singleton):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    def __init__(self, tox, screen):
        """
        :param tox: tox instance
        :param screen: ref to main screen
        """
        contact.Contact.__init__(self,
                                 tox.self_get_name(),
                                 tox.self_get_status_message(),
                                 screen.user_info,
                                 tox.self_get_address())
        Singleton.__init__(self)
        self._screen = screen
        self._messages = screen.messages
        self._tox = tox
        self._file_transfers = {}  # dict of file transfers. key - tuple (friend_number, file_number)
        self._call = calls.AV(tox.AV)  # object with data about calls
        self._incoming_calls = set()
        self._load_history = True
        settings = Settings.get_instance()
        self._show_online = settings['show_online_friends']
        screen.online_contacts.setCurrentIndex(int(self._show_online))
        aliases = settings['friends_aliases']
        data = tox.self_get_friend_list()
        self._history = History(tox.self_get_public_key())  # connection to db
        self._friends, self._active_friend = [], -1
        for i in data:  # creates list of friends
            tox_id = tox.friend_get_public_key(i)
            try:
                alias = list(filter(lambda x: x[0] == tox_id, aliases))[0][1]
            except:
                alias = ''
            item = self.create_friend_item()
            name = alias or tox.friend_get_name(i) or tox_id
            status_message = tox.friend_get_status_message(i)
            if not self._history.friend_exists_in_db(tox_id):
                self._history.add_friend_to_db(tox_id)
            message_getter = self._history.messages_getter(tox_id)
            friend = Friend(message_getter, i, name, status_message, item, tox_id)
            friend.set_alias(alias)
            self._friends.append(friend)
        self.filtration(self._show_online)

    # -----------------------------------------------------------------------------------------------------------------
    # Edit current user's data
    # -----------------------------------------------------------------------------------------------------------------

    def change_status(self):
        """
        Changes status of user (online, away, busy)
        """
        if self._status is not None:
            self.set_status((self._status + 1) % 3)

    def set_status(self, status):
        super(Profile, self).set_status(status)
        if status is not None:
            self._tox.self_set_status(status)

    def set_name(self, value):
        if self.name == value:
            return
        tmp = self.name
        super(Profile, self).set_name(value.encode('utf-8'))
        self._tox.self_set_name(self._name.encode('utf-8'))
        message = QtGui.QApplication.translate("MainWindow", 'User {} is now known as {}', None,
                                               QtGui.QApplication.UnicodeUTF8)
        message = message.format(tmp, value)
        for friend in self._friends:
            friend.append_message(InfoMessage(message, time.time()))
        if self._active_friend + 1:
            self.create_message_item(message, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()

    def set_status_message(self, value):
        super(Profile, self).set_status_message(value)
        self._tox.self_set_status_message(self._status_message.encode('utf-8'))

    def new_nospam(self):
        """Sets new nospam part of tox id"""
        import random
        self._tox.self_set_nospam(random.randint(0, 4294967295))  # no spam - uint32
        self._tox_id = self._tox.self_get_address()
        return self._tox_id

    # -----------------------------------------------------------------------------------------------------------------
    # Filtration
    # -----------------------------------------------------------------------------------------------------------------

    def filtration(self, show_online=True, filter_str=''):
        """
        Filtration of friends list
        :param show_online: show online only contacts
        :param filter_str: show contacts which name contains this substring
        """
        filter_str = filter_str.lower()
        settings = Settings.get_instance()
        for index, friend in enumerate(self._friends):
            friend.visibility = (friend.status is not None or not show_online) and (filter_str in friend.name.lower())
            friend.visibility = friend.visibility or friend.messages or friend.actions
            if friend.visibility:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250,
                                                                               40 if settings['compact_mode'] else 70))
            else:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 0))
        self._show_online, self._filter_string = show_online, filter_str
        settings['show_online_friends'] = self._show_online
        settings.save()

    def update_filtration(self):
        """
        Update list of contacts when 1 of friends change connection status
        """
        self.filtration(self._show_online, self._filter_string)

    def get_friend_by_number(self, num):
        return list(filter(lambda x: x.number == num, self._friends))[0]

    def get_friend(self, num):
        return self._friends[num]

    # -----------------------------------------------------------------------------------------------------------------
    # Work with active friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_active(self):
        return self._active_friend

    def set_active(self, value=None):
        """
        Change current active friend or update info
        :param value: number of new active friend in friend's list or None to update active user's data
        """
        if value is None and self._active_friend == -1:  # nothing to update
            return
        if value == -1:  # all friends were deleted
            self._screen.account_name.setText('')
            self._screen.account_status.setText('')
            self._active_friend = -1
            self._screen.account_avatar.setHidden(True)
            self._messages.clear()
            self._screen.messageEdit.clear()
            return
        try:
            self.send_typing(False)
            self._screen.typing.setVisible(False)
            if value is not None:
                if self._active_friend + 1:
                    try:
                        self._friends[self._active_friend].curr_text = self._screen.messageEdit.toPlainText()
                    except:
                        pass
                self._active_friend = value
                friend = self._friends[value]
                self._friends[value].reset_messages()
                self._screen.messageEdit.setPlainText(friend.curr_text)
                self._messages.clear()
                friend.load_corr()
                messages = friend.get_corr()[-PAGE_SIZE:]
                self._load_history = False
                for message in messages:
                    if message.get_type() <= 1:
                        data = message.get_data()
                        self.create_message_item(data[0],
                                                 data[2],
                                                 data[1],
                                                 data[3])
                    elif message.get_type() == MESSAGE_TYPE['FILE_TRANSFER']:
                        if message.get_status() is None:
                            self.create_unsent_file_item(message)
                            continue
                        item = self.create_file_transfer_item(message)
                        if message.get_status() in ACTIVE_FILE_TRANSFERS:  # active file transfer
                            try:
                                ft = self._file_transfers[(message.get_friend_number(), message.get_file_number())]
                                ft.set_state_changed_handler(item.update)
                                ft.signal()
                            except:
                                print('Incoming not started transfer - no info found')
                    elif message.get_type() == MESSAGE_TYPE['INLINE']:  # inline
                        self.create_inline_item(message.get_data())
                    else:  # info message
                        data = message.get_data()
                        self.create_message_item(data[0],
                                                 data[2],
                                                 '',
                                                 data[3])
                self._messages.scrollToBottom()
                self._load_history = True
                if value in self._call:
                    self._screen.active_call()
                elif value in self._incoming_calls:
                    self._screen.incoming_call()
                else:
                    self._screen.call_finished()
            else:
                friend = self._friends[self._active_friend]

            self._screen.account_name.setText(friend.name)
            self._screen.account_status.setText(friend.status_message)
            avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(friend.tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
            if not os.path.isfile(avatar_path):  # load default image
                avatar_path = curr_directory() + '/images/avatar.png'
            os.chdir(os.path.dirname(avatar_path))
            pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
            pixmap.load(avatar_path)
            self._screen.account_avatar.setScaledContents(False)
            self._screen.account_avatar.setPixmap(pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))
            self._screen.account_avatar.repaint()  # comment?
            self.update_filtration()
        except Exception as ex:  # no friend found. ignore
            log('Friend value: ' + str(value))
            log('Error: ' + str(ex))
            raise

    active_friend = property(get_active, set_active)

    def get_last_message(self):
        return self._friends[self._active_friend].get_last_message_text()

    def get_active_number(self):
        return self._friends[self._active_friend].number if self._active_friend + 1 else -1

    def get_active_name(self):
        return self._friends[self._active_friend].name if self._active_friend + 1 else ''

    def is_active_online(self):
        return self._active_friend + 1 and self._friends[self._active_friend].status is not None

    def new_name(self, number, name):
        friend = self.get_friend_by_number(number)
        tmp = friend.name
        friend.set_name(name)
        name = str(name, 'utf-8')
        if friend.name == name and tmp != name:
            message = QtGui.QApplication.translate("MainWindow", 'User {} is now known as {}', None, QtGui.QApplication.UnicodeUTF8)
            message = message.format(tmp, name)
            friend.append_message(InfoMessage(message, time.time()))
            friend.actions = True
            if number == self.get_active_number():
                self.create_message_item(message, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
                self._messages.scrollToBottom()
            self.set_active(None)

    def update(self):
        if self._active_friend + 1:
            self.set_active(self._active_friend)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend connection status callbacks
    # -----------------------------------------------------------------------------------------------------------------

    def send_files(self, friend_number):
        friend = self.get_friend_by_number(friend_number)
        files = friend.get_unsent_files()
        try:
            for fl in files:
                data = fl.get_data()
                if data[1] is not None:
                    self.send_inline(data[1], data[0], friend_number, True)
                else:
                    self.send_file(data[0], friend_number, True)
            friend.clear_unsent_files()
            if friend_number == self.get_active_number():
                self.update()
        except Exception as ex:
            print('Exception in file sending: ' + str(ex))

    def friend_exit(self, friend_number):
        """
        Friend with specified number quit
        """
        # TODO: fix and add full file resuming support
        self.get_friend_by_number(friend_number).status = None
        self.friend_typing(friend_number, False)
        if friend_number in self._call:
            self._call.finish_call(friend_number, True)

    # -----------------------------------------------------------------------------------------------------------------
    # Typing notifications
    # -----------------------------------------------------------------------------------------------------------------

    def send_typing(self, typing):
        """
        Send typing notification to a friend
        """
        if Settings.get_instance()['typing_notifications'] and self._active_friend + 1:
            friend = self._friends[self._active_friend]
            if friend.status is not None:
                self._tox.self_set_typing(friend.number, typing)

    def friend_typing(self, friend_number, typing):
        """
        Display incoming typing notification
        """
        if friend_number == self.get_active_number():
            self._screen.typing.setVisible(typing)

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def receipt(self):
        i = 0
        while i < self._messages.count() and not self._messages.itemWidget(self._messages.item(i)).mark_as_sent():
            i += 1

    def send_messages(self, friend_number):
        """
        Send 'offline' messages to friend
        """
        friend = self.get_friend_by_number(friend_number)
        friend.load_corr()
        messages = friend.get_unsent_messages()
        try:
            for message in messages:
                self.split_and_send(friend_number, message.get_data()[-1], message.get_data()[0].encode('utf-8'))
                friend.inc_receipts()
        except:
            pass

    def split_and_send(self, number, message_type, message):
        """
        Message splitting
        :param number: friend's number
        :param message_type: type of message
        :param message: message text
        """
        while len(message) > TOX_MAX_MESSAGE_LENGTH:
            size = TOX_MAX_MESSAGE_LENGTH * 4 / 5
            last_part = message[size:TOX_MAX_MESSAGE_LENGTH]
            if ' ' in last_part:
                index = last_part.index(' ')
            elif ',' in last_part:
                index = last_part.index(',')
            elif '.' in last_part:
                index = last_part.index('.')
            else:
                index = TOX_MAX_MESSAGE_LENGTH - size - 1
            index += size + 1
            self._tox.friend_send_message(number, message_type, message[:index])
            message = message[index:]
        self._tox.friend_send_message(number, message_type, message)

    def new_message(self, friend_num, message_type, message):
        """
        Current user gets new message
        :param friend_num: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        if friend_num == self.get_active_number():  # add message to list
            t = time.time()
            self.create_message_item(message, t, MESSAGE_OWNER['FRIEND'], message_type)
            self._messages.scrollToBottom()
            self._friends[self._active_friend].append_message(
                TextMessage(message, MESSAGE_OWNER['FRIEND'], t, message_type))
        else:
            friend = self.get_friend_by_number(friend_num)
            friend.inc_messages()
            friend.append_message(
                TextMessage(message, MESSAGE_OWNER['FRIEND'], time.time(), message_type))
            if not friend.visibility:
                self.update_filtration()

    def send_message(self, text):
        """
        Send message to active friend
        :param text: message text
        """
        if text.startswith('/plugin '):
            plugin_support.PluginLoader.get_instance().command(text[8:])
            self._screen.messageEdit.clear()
        elif text and self._active_friend + 1:
            text = ''.join(c if c <= '\u10FFFF' else '\u25AF' for c in text)
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            friend = self._friends[self._active_friend]
            friend.inc_receipts()
            if friend.status is not None:
                self.split_and_send(friend.number, message_type, text.encode('utf-8'))
            t = time.time()
            self.create_message_item(text, t, MESSAGE_OWNER['NOT_SENT'], message_type)
            self._screen.messageEdit.clear()
            self._messages.scrollToBottom()
            friend.append_message(TextMessage(text, MESSAGE_OWNER['NOT_SENT'], t, message_type))

    def delete_message(self, time):
        friend = self._friends[self._active_friend]
        friend.delete_message(time)
        self._history.delete_message(friend.tox_id, time)
        self.update()

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def save_history(self):
        """
        Save history to db
        """
        s = Settings.get_instance()
        if hasattr(self, '_history'):
            if s['save_history']:
                for friend in self._friends:
                    if not self._history.friend_exists_in_db(friend.tox_id):
                        self._history.add_friend_to_db(friend.tox_id)
                    if not s['save_unsent_only']:
                        messages = friend.get_corr_for_saving()
                    else:
                        messages = friend.get_unsent_messages_for_saving()
                        self._history.delete_messages(friend.tox_id)
                    self._history.save_messages_to_db(friend.tox_id, messages)
                    unsent_messages = friend.get_unsent_messages()
                    unsent_time = unsent_messages[0].get_data()[2] if len(unsent_messages) else time.time() + 1
                    self._history.update_messages(friend.tox_id, unsent_time)
            self._history.save()
            del self._history

    def clear_history(self, num=None, save_unsent=False):
        """
        Clear chat history
        """
        if num is not None:
            friend = self._friends[num]
            friend.clear_corr(save_unsent)
            if self._history.friend_exists_in_db(friend.tox_id):
                self._history.delete_messages(friend.tox_id)
                self._history.delete_friend_from_db(friend.tox_id)
        else:  # clear all history
            for number in range(len(self._friends)):
                self.clear_history(number, save_unsent)
        if num is None or num == self.get_active_number():
            self.update()

    def load_history(self):
        """
        Tries to load next part of messages
        """
        if not self._load_history:
            return
        self._load_history = False
        friend = self._friends[self._active_friend]
        friend.load_corr(False)
        data = friend.get_corr()
        if not data:
            return
        data.reverse()
        data = data[self._messages.count():self._messages.count() + PAGE_SIZE]
        for message in data:
            if message.get_type() <= 1:  # text message
                data = message.get_data()
                self.create_message_item(data[0],
                                         data[2],
                                         data[1],
                                         data[3],
                                         False)
            elif message.get_type() == MESSAGE_TYPE['FILE_TRANSFER']:
                if message.get_status() is None:
                    self.create_unsent_file_item(message)
                    continue
                item = self.create_file_transfer_item(message, False)
                if message.get_status() in ACTIVE_FILE_TRANSFERS:  # active file transfer
                    try:
                        ft = self._file_transfers[(message.get_friend_number(), message.get_file_number())]
                        ft.set_state_changed_handler(item.update)
                        ft.signal()
                    except:
                        print('Incoming not started transfer - no info found')
            elif message.get_type() == MESSAGE_TYPE['INLINE']:  # inline
                self.create_inline_item(message.get_data())
            else:  # info message
                data = message.get_data()
                self.create_message_item(data[0],
                                         data[2],
                                         '',
                                         data[3])
        self._load_history = True

    def export_history(self, directory):
        self._history.export(directory)

    # -----------------------------------------------------------------------------------------------------------------
    # Factories for friend, message and file transfer items
    # -----------------------------------------------------------------------------------------------------------------

    def create_friend_item(self):
        """
        Method-factory
        :return: new widget for friend instance
        """
        item = ContactItem()
        elem = QtGui.QListWidgetItem(self._screen.friends_list)
        elem.setSizeHint(QtCore.QSize(250, item.height()))
        self._screen.friends_list.addItem(elem)
        self._screen.friends_list.setItemWidget(elem, item)
        return item

    def create_message_item(self, text, time, owner, message_type, append=True):
        if message_type == MESSAGE_TYPE['INFO_MESSAGE']:
            name = ''
        elif owner == MESSAGE_OWNER['FRIEND']:
            name = self.get_active_name()
        else:
            name = self._name
        item = MessageItem(text, time, name, owner != MESSAGE_OWNER['NOT_SENT'], message_type, self._messages)
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

    def create_file_transfer_item(self, tm, append=True):
        data = list(tm.get_data())
        data[3] = self.get_friend_by_number(data[4]).name if data[3] else self._name
        data.append(self._messages.width())
        item = FileTransferItem(*data)
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)
        return item

    def create_unsent_file_item(self, message, append=True):
        data = message.get_data()
        item = UnsentFileItem(os.path.basename(data[0]),
                              os.path.getsize(data[0]) if data[1] is None else len(data[1]),
                              self.name,
                              data[2],
                              self._messages.width())
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

    def create_inline_item(self, data, append=True):
        elem = QtGui.QListWidgetItem()
        item = InlineImageItem(data, self._messages.width(), elem)
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

    # -----------------------------------------------------------------------------------------------------------------
    # Work with friends (remove, block, set alias, get public key)
    # -----------------------------------------------------------------------------------------------------------------

    def set_alias(self, num):
        """
        Set new alias for friend
        """
        friend = self._friends[num]
        name = friend.name
        dialog = QtGui.QApplication.translate('MainWindow',
                                              "Enter new alias for friend {} or leave empty to use friend's name:",
                                              None, QtGui.QApplication.UnicodeUTF8)
        dialog = dialog.format(name)
        title = QtGui.QApplication.translate('MainWindow',
                                             'Set alias',
                                             None, QtGui.QApplication.UnicodeUTF8)
        text, ok = QtGui.QInputDialog.getText(None,
                                              title,
                                              dialog,
                                              QtGui.QLineEdit.Normal,
                                              name)
        if ok:
            settings = Settings.get_instance()
            aliases = settings['friends_aliases']
            if text:
                friend.name = bytes(text, 'utf-8')
                try:
                    index = list(map(lambda x: x[0], aliases)).index(friend.tox_id)
                    aliases[index] = (friend.tox_id, text)
                except:
                    aliases.append((friend.tox_id, text))
                friend.set_alias(text)
            else:  # use default name
                friend.name = bytes(self._tox.friend_get_name(friend.number), 'utf-8')
                friend.set_alias('')
                try:
                    index = list(map(lambda x: x[0], aliases)).index(friend.tox_id)
                    del aliases[index]
                except:
                    pass
            settings.save()
        if num == self.get_active_number():
            self.update()

    def friend_public_key(self, num):
        return self._friends[num].tox_id

    def delete_friend(self, num):
        """
        Removes friend from contact list
        :param num: number of friend in list
        """
        friend = self._friends[num]
        settings = Settings.get_instance()
        try:
            index = list(map(lambda x: x[0], settings['friends_aliases'])).index(friend.tox_id)
            del settings['friends_aliases'][index]
        except:
            pass
        if friend.tox_id in settings['notes']:
            del settings['notes'][friend.tox_id]
        settings.save()
        self.clear_history(num)
        if self._history.friend_exists_in_db(friend.tox_id):
            self._history.delete_friend_from_db(friend.tox_id)
        self._tox.friend_delete(friend.number)
        del self._friends[num]
        self._screen.friends_list.takeItem(num)
        if num == self._active_friend:  # active friend was deleted
            if not len(self._friends):  # last friend was deleted
                self.set_active(-1)
            else:
                self.set_active(0)
        data = self._tox.get_savedata()
        ProfileHelper.get_instance().save_profile(data)

    def add_friend(self, tox_id):
        """
        Adds friend to list
        """
        num = self._tox.friend_add_norequest(tox_id)  # num - friend number
        item = self.create_friend_item()
        try:
            if not self._history.friend_exists_in_db(tox_id):
                self._history.add_friend_to_db(tox_id)
            message_getter = self._history.messages_getter(tox_id)
        except Exception as ex:  # something is wrong
            log('Accept friend request failed! ' + str(ex))
            message_getter = None
        friend = Friend(message_getter, num, tox_id, '', item, tox_id)
        self._friends.append(friend)

    def block_user(self, tox_id):
        """
        Block user with specified tox id (or public key) - delete from friends list and ignore friend requests
        """
        tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
        if tox_id == self.tox_id[:TOX_PUBLIC_KEY_SIZE * 2]:
            return
        settings = Settings.get_instance()
        if tox_id not in settings['blocked']:
            settings['blocked'].append(tox_id)
            settings.save()
        try:
            num = self._tox.friend_by_public_key(tox_id)
            self.delete_friend(num)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)
        except:  # not in friend list
            pass

    def unblock_user(self, tox_id, add_to_friend_list):
        """
        Unblock user
        :param tox_id: tox id of contact
        :param add_to_friend_list: add this contact to friend list or not
        """
        s = Settings.get_instance()
        s['blocked'].remove(tox_id)
        s.save()
        if add_to_friend_list:
            self.add_friend(tox_id)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend requests
    # -----------------------------------------------------------------------------------------------------------------

    def send_friend_request(self, tox_id, message):
        """
        Function tries to send request to contact with specified id
        :param tox_id: id of new contact or tox dns 4 value
        :param message: additional message
        :return: True on success else error string
        """
        try:
            message = message or 'Hello! Add me to your contact list please'
            if '@' in tox_id:  # value like groupbot@toxme.io
                tox_id = tox_dns(tox_id)
                if tox_id is None:
                    raise Exception('TOX DNS lookup failed')
            if len(tox_id) == TOX_PUBLIC_KEY_SIZE * 2:  # public key
                self.add_friend(tox_id)
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Friend added", None, QtGui.QApplication.UnicodeUTF8))
                text = (QtGui.QApplication.translate("MainWindow", 'Friend added without sending friend request', None, QtGui.QApplication.UnicodeUTF8))
                msgBox.setText(text)
                msgBox.exec_()
            else:
                result = self._tox.friend_add(tox_id, message.encode('utf-8'))
                tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
                item = self.create_friend_item()
                if not self._history.friend_exists_in_db(tox_id):
                    self._history.add_friend_to_db(tox_id)
                message_getter = self._history.messages_getter(tox_id)
                friend = Friend(message_getter, result, tox_id, '', item, tox_id)
                self._friends.append(friend)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)
            return True
        except Exception as ex:  # wrong data
            log('Friend request failed with ' + str(ex))
            return str(ex)

    def process_friend_request(self, tox_id, message):
        """
        Accept or ignore friend request
        :param tox_id: tox id of contact
        :param message: message
        """
        try:
            text = QtGui.QApplication.translate('MainWindow', 'User {} wants to add you to contact list. Message:\n{}', None, QtGui.QApplication.UnicodeUTF8)
            info = text.format(tox_id, message)
            fr_req = QtGui.QApplication.translate('MainWindow', 'Friend request', None, QtGui.QApplication.UnicodeUTF8)
            reply = QtGui.QMessageBox.question(None, fr_req, info, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:  # accepted
                self.add_friend(tox_id)
                data = self._tox.get_savedata()
                ProfileHelper.get_instance().save_profile(data)
        except Exception as ex:  # something is wrong
            log('Accept friend request failed! ' + str(ex))

    # -----------------------------------------------------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------------------------------------------------

    def reset(self, restart):
        """
        Recreate tox instance
        :param restart: method which calls restart and returns new tox instance
        """
        # TODO: file transfers!!
        for key in list(self._file_transfers.keys()):
            self._file_transfers[key].cancelled()
            del self._file_transfers[key]
        self._call.stop()
        del self._tox
        self._tox = restart()
        self.status = None
        for friend in self._friends:
            friend.status = None
        self.update_filtration()

    def close(self):
        if hasattr(self, '_call'):
            self._call.stop()
            del self._call
        for i in range(len(self._friends)):
            del self._friends[0]

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def incoming_file_transfer(self, friend_number, file_number, size, file_name):
        """
        New transfer
        :param friend_number: number of friend who sent file
        :param file_number: file number
        :param size: file size in bytes
        :param file_name: file name without path
        """
        settings = Settings.get_instance()
        friend = self.get_friend_by_number(friend_number)
        auto = settings['allow_auto_accept'] and friend.tox_id in settings['auto_accept_from_friends']
        inline = (file_name in ALLOWED_FILES) and settings['allow_inline']
        if inline and size < 1024 * 1024:
            self.accept_transfer(None, '', friend_number, file_number, size, True)
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['RUNNING'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)

        elif auto:
            path = settings['auto_accept_path'] or curr_directory()
            if not os.path.isdir(path):
                path = curr_directory()
            new_file_name, i = file_name, 1
            while os.path.isfile(path + '/' + new_file_name):  # file with same name already exists
                if '.' in file_name:  # has extension
                    d = file_name.rindex('.')
                else:  # no extension
                    d = len(file_name)
                new_file_name = file_name[:d] + ' ({})'.format(i) + file_name[d:]
                i += 1
            self.accept_transfer(None, path + '/' + new_file_name, friend_number, file_number, size)
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['RUNNING'],
                                 size,
                                 new_file_name,
                                 friend_number,
                                 file_number)
        else:
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['INCOMING_NOT_STARTED'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)
        if friend_number == self.get_active_number():
            item = self.create_file_transfer_item(tm)
            if (inline and size < 1024 * 1024) or auto:
                self._file_transfers[(friend_number, file_number)].set_state_changed_handler(item.update)
            self._messages.scrollToBottom()
        else:
            friend.actions = True

        friend.append_message(tm)

    def cancel_transfer(self, friend_number, file_number, already_cancelled=False):
        """
        Stop transfer
        :param friend_number: number of friend
        :param file_number: file number
        :param already_cancelled: was cancelled by friend
        """
        i = self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                          TOX_FILE_TRANSFER_STATE['CANCELLED'])
        if (friend_number, file_number) in self._file_transfers:
            tr = self._file_transfers[(friend_number, file_number)]
            if not already_cancelled:
                tr.cancel()
            else:
                tr.cancelled()
            if (friend_number, file_number) in self._file_transfers:
                del tr
                del self._file_transfers[(friend_number, file_number)]
        else:
            if not already_cancelled:
                self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
            if friend_number == self.get_active_number():
                tmp = self._messages.count() + i
                if tmp >= 0:
                    self._messages.itemWidget(self._messages.item(tmp)).update(TOX_FILE_TRANSFER_STATE['CANCELLED'],
                                                                               0, -1)

    def cancel_not_started_transfer(self, time):
        self._friends[self._active_friend].delete_one_unsent_file(time)
        self.update()

    def pause_transfer(self, friend_number, file_number, by_friend=False):
        """
        Pause transfer with specified data
        """
        tr = self._file_transfers[(friend_number, file_number)]
        tr.pause(by_friend)
        t = TOX_FILE_TRANSFER_STATE['PAUSED_BY_FRIEND'] if by_friend else TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']
        self.get_friend_by_number(friend_number).update_transfer_data(file_number, t)

    def resume_transfer(self, friend_number, file_number, by_friend=False):
        """
        Resume transfer with specified data
        """
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      TOX_FILE_TRANSFER_STATE['RUNNING'])
        # if (friend_number, file_number) not in self._file_transfers:
        #     print self._file_transfers
        #     print (friend_number, file_number)
        #     return
        tr = self._file_transfers[(friend_number, file_number)]
        if by_friend:
            tr.state = TOX_FILE_TRANSFER_STATE['RUNNING']
            tr.signal()
        else:  # send seek control?
            tr.send_control(TOX_FILE_CONTROL['RESUME'])

    def accept_transfer(self, item, path, friend_number, file_number, size, inline=False):
        """
        :param item: transfer item.
        :param path: path for saving
        :param friend_number: friend number
        :param file_number: file number
        :param size: file size
        :param inline: is inline image
        """
        if not inline:
            rt = ReceiveTransfer(path, self._tox, friend_number, size, file_number)
        else:
            rt = ReceiveToBuffer(self._tox, friend_number, size, file_number)
        self._file_transfers[(friend_number, file_number)] = rt
        self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['RESUME'])
        if item is not None:
            rt.set_state_changed_handler(item.update)
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      TOX_FILE_TRANSFER_STATE['RUNNING'])

    def send_screenshot(self, data):
        """
        Send screenshot to current active friend
        :param data: raw data - png
        """
        self.send_inline(data, 'toxygen_inline.png')

    def send_sticker(self, path):
        with open(path, 'rb') as fl:
            data = fl.read()
        self.send_inline(data, 'sticker.png')

    def send_inline(self, data, file_name, friend_number=None, is_resend=False):
        friend_number = friend_number or self.get_active_number()
        friend = self.get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            m = UnsentFile(file_name, data, time.time())
            friend.append_message(m)
            self.update()
            return
        elif friend.status is None and is_resend:
            raise RuntimeError()
        st = SendFromBuffer(self._tox, friend.number, data, file_name)
        self._file_transfers[(friend.number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_OWNER['ME'],
                             time.time(),
                             TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED'],
                             len(data),
                             file_name,
                             friend.number,
                             st.get_file_number())
        item = self.create_file_transfer_item(tm)
        friend.append_message(tm)
        st.set_state_changed_handler(item.update)
        self._messages.scrollToBottom()

    def send_file(self, path, number=None, is_resend=False):
        """
        Send file to current active friend
        :param path: file path
        :param number: friend_number
        :param is_resend: is 'offline' message
        """
        friend_number = number or self.get_active_number()
        friend = self.get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            m = UnsentFile(path, None, time.time())
            friend.append_message(m)
            self.update()
            return
        elif friend.status is None and is_resend:
            print('Error in sending')
            raise RuntimeError()
        st = SendTransfer(path, self._tox, friend_number)
        self._file_transfers[(friend_number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_OWNER['ME'],
                             time.time(),
                             TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED'],
                             os.path.getsize(path),
                             os.path.basename(path),
                             friend_number,
                             st.get_file_number())
        item = self.create_file_transfer_item(tm)
        st.set_state_changed_handler(item.update)
        self._friends[self._active_friend].append_message(tm)
        self._messages.scrollToBottom()

    def incoming_chunk(self, friend_number, file_number, position, data):
        """
        Incoming chunk
        """
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.write_chunk(position, data)
            if transfer.state not in ACTIVE_FILE_TRANSFERS:  # finished or cancelled
                if type(transfer) is ReceiveAvatar:
                    self.get_friend_by_number(friend_number).load_avatar()
                    self.set_active(None)
                elif type(transfer) is ReceiveToBuffer:  # inline image
                    print('inline')
                    inline = InlineImage(transfer.get_data())
                    i = self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                      TOX_FILE_TRANSFER_STATE['FINISHED'],
                                                                                      inline)
                    if friend_number == self.get_active_number():
                        count = self._messages.count()
                        if count + i + 1 >= 0:
                            elem = QtGui.QListWidgetItem()
                            item = InlineImageItem(transfer.get_data(), self._messages.width(), elem)
                            elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
                            self._messages.insertItem(count + i + 1, elem)
                            self._messages.setItemWidget(elem, item)
                else:
                    self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                  TOX_FILE_TRANSFER_STATE['FINISHED'])
                del self._file_transfers[(friend_number, file_number)]

    def outgoing_chunk(self, friend_number, file_number, position, size):
        """
        Outgoing chunk
        """
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.send_chunk(position, size)
            if transfer.state not in ACTIVE_FILE_TRANSFERS:  # finished or cancelled
                del self._file_transfers[(friend_number, file_number)]
                if type(transfer) is not SendAvatar:
                    if type(transfer) is SendFromBuffer and Settings.get_instance()['allow_inline']:  # inline
                        inline = InlineImage(transfer.get_data())
                        print('inline')
                        i = self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                          TOX_FILE_TRANSFER_STATE[
                                                                                              'FINISHED'],
                                                                                          inline)
                        if friend_number == self.get_active_number():
                            count = self._messages.count()
                            if count + i + 1 >= 0:
                                elem = QtGui.QListWidgetItem()
                                item = InlineImageItem(transfer.get_data(), self._messages.width(), elem)
                                elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
                                self._messages.insertItem(count + i + 1, elem)
                                self._messages.setItemWidget(elem, item)
                    else:
                        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                      TOX_FILE_TRANSFER_STATE['FINISHED'])

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars support
    # -----------------------------------------------------------------------------------------------------------------

    def send_avatar(self, friend_number):
        """
        :param friend_number: number of friend who should get new avatar
        """
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        if not os.path.isfile(avatar_path):  # reset image
            avatar_path = None
        sa = SendAvatar(avatar_path, self._tox, friend_number)
        self._file_transfers[(friend_number, sa.get_file_number())] = sa

    def incoming_avatar(self, friend_number, file_number, size):
        """
        Friend changed avatar
        :param friend_number: friend number
        :param file_number: file number
        :param size: size of avatar or 0 (default avatar)
        """
        ra = ReceiveAvatar(self._tox, friend_number, size, file_number)
        if ra.state != TOX_FILE_TRANSFER_STATE['CANCELLED']:
            self._file_transfers[(friend_number, file_number)] = ra
        else:
            self.get_friend_by_number(friend_number).load_avatar()
            if self.get_active_number() == friend_number:
                self.set_active(None)

    def reset_avatar(self):
        super(Profile, self).reset_avatar()
        for friend in filter(lambda x: x.status is not None, self._friends):
            self.send_avatar(friend.number)

    def set_avatar(self, data):
        super(Profile, self).set_avatar(data)
        for friend in filter(lambda x: x.status is not None, self._friends):
            self.send_avatar(friend.number)

    # -----------------------------------------------------------------------------------------------------------------
    # AV support
    # -----------------------------------------------------------------------------------------------------------------

    def get_call(self):
        return self._call

    call = property(get_call)

    def call_click(self, audio=True, video=False):
        """User clicked audio button in main window"""
        num = self.get_active_number()
        if num not in self._call and self.is_active_online():  # start call
            self._call(num, audio, video)
            self._screen.active_call()
            if video:
                text = QtGui.QApplication.translate("incoming_call", "Outgoing video call", None,
                                                    QtGui.QApplication.UnicodeUTF8)
            else:
                text = QtGui.QApplication.translate("incoming_call", "Outgoing audio call", None,
                                                    QtGui.QApplication.UnicodeUTF8)
            self._friends[self._active_friend].append_message(InfoMessage(text, time.time()))
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()
        elif num in self._call:  # finish or cancel call if you call with active friend
            self.stop_call(num, False)

    def incoming_call(self, audio, video, friend_number):
        """
        Incoming call from friend. Only audio is supported now
        """
        friend = self.get_friend_by_number(friend_number)
        if video:
            text = QtGui.QApplication.translate("incoming_call", "Incoming video call", None,
                                                QtGui.QApplication.UnicodeUTF8)
        else:
            text = QtGui.QApplication.translate("incoming_call", "Incoming audio call", None,
                                                QtGui.QApplication.UnicodeUTF8)
        friend.append_message(InfoMessage(text, time.time()))
        self._incoming_calls.add(friend_number)
        if friend_number == self.get_active_number():
            self._screen.incoming_call()
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()
        else:
            friend.actions = True
        self._call_widget = avwidgets.IncomingCallWidget(friend_number, text, friend.name)
        self._call_widget.set_pixmap(friend.get_pixmap())
        self._call_widget.show()

    def accept_call(self, friend_number, audio, video):
        """
        Accept incoming call with audio or video
        """
        self._call.accept_call(friend_number, audio, video)
        self._screen.active_call()
        self._incoming_calls.remove(friend_number)
        if hasattr(self, '_call_widget'):
            del self._call_widget

    def stop_call(self, friend_number, by_friend):
        """
        Stop call with friend
        """
        if friend_number in self._incoming_calls:
            self._incoming_calls.remove(friend_number)
            text = QtGui.QApplication.translate("incoming_call", "Call declined", None, QtGui.QApplication.UnicodeUTF8)
        else:
            text = QtGui.QApplication.translate("incoming_call", "Call finished", None, QtGui.QApplication.UnicodeUTF8)
        self._screen.call_finished()
        self._call.finish_call(friend_number, by_friend)  # finish or decline call
        if hasattr(self, '_call_widget'):
            del self._call_widget
        friend = self.get_friend_by_number(friend_number)
        friend.append_message(InfoMessage(text, time.time()))
        if friend_number == self.get_active_number():
            self.create_message_item(text, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()


def tox_factory(data=None, settings=None):
    """
    :param data: user data from .tox file. None = no saved data, create new profile
    :param settings: current profile settings. None = default settings will be used
    :return: new tox instance
    """
    if settings is None:
        settings = Settings.get_default_settings()
    tox_options = Tox.options_new()
    tox_options.contents.udp_enabled = settings['udp_enabled']
    tox_options.contents.proxy_type = settings['proxy_type']
    tox_options.contents.proxy_host = bytes(settings['proxy_host'], 'UTF-8')
    tox_options.contents.proxy_port = settings['proxy_port']
    tox_options.contents.start_port = settings['start_port']
    tox_options.contents.end_port = settings['end_port']
    tox_options.contents.tcp_port = settings['tcp_port']
    if data:  # load existing profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['TOX_SAVE']
        tox_options.contents.savedata_data = c_char_p(data)
        tox_options.contents.savedata_length = len(data)
    else:  # create new profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['NONE']
        tox_options.contents.savedata_data = None
        tox_options.contents.savedata_length = 0
    return Tox(tox_options)
