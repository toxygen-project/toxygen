from PyQt5 import uic, QtWidgets
import utils.util as util
from ui.widgets import *


class GroupInviteItem(QtWidgets.QWidget):

    def __init__(self, parent, chat_name, avatar, friend_name):
        super().__init__(parent)
        uic.loadUi(util.get_views_path('gc_invite_item'), self)

        self.groupNameLabel.setText(chat_name)
        self.friendNameLabel.setText(friend_name)
        self.friendAvatarLabel.setPixmap(avatar)

    def is_selected(self):
        return self.selectCheckBox.isChecked()

    def subscribe_checked_event(self, callback):
        self.selectCheckBox.clicked.connect(callback)


class GroupInvitesScreen(CenteredWidget):

    def __init__(self, groups_service, profile, contacts_provider):
        super().__init__()
        self._groups_service = groups_service
        self._profile = profile
        self._contacts_provider = contacts_provider

        uic.loadUi(util.get_views_path('group_invites_screen'), self)

        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self._refresh_invites_list()

        self.nickLineEdit.setText(self._profile.name)
        self.statusComboBox.setCurrentIndex(self._profile.status or 0)

        self.nickLineEdit.textChanged.connect(self._nick_changed)
        self.acceptPushButton.clicked.connect(self._accept_invites)
        self.declinePushButton.clicked.connect(self._decline_invites)

        self.invitesListWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self._update_buttons_state()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Group chat invites'))
        self.noInvitesLabel.setText(util_ui.tr('No group invites found'))
        self.acceptPushButton.setText(util_ui.tr('Accept'))
        self.declinePushButton.setText(util_ui.tr('Decline'))
        self.statusComboBox.addItem(util_ui.tr('Online'))
        self.statusComboBox.addItem(util_ui.tr('Away'))
        self.statusComboBox.addItem(util_ui.tr('Busy'))
        self.nickLineEdit.setPlaceholderText(util_ui.tr('Your nick in chat'))
        self.passwordLineEdit.setPlaceholderText(util_ui.tr('Optional password'))

    def _get_friend(self, public_key):
        return self._contacts_provider.get_friend_by_public_key(public_key)

    def _accept_invites(self):
        nick = self.nickLineEdit.text()
        password = self.passwordLineEdit.text()
        status = self.statusComboBox.currentIndex()

        selected_invites = self._get_selected_invites()
        for invite in selected_invites:
            self._groups_service.accept_group_invite(invite, nick, status, password)

        self._refresh_invites_list()

    def _decline_invites(self):
        selected_invites = self._get_selected_invites()
        for invite in selected_invites:
            self._groups_service.decline_group_invite(invite)

        self._refresh_invites_list()

    def _get_selected_invites(self):
        all_invites = self._groups_service.get_group_invites()
        selected = []
        items_count = len(all_invites)
        for index in range(items_count):
            list_item = self.invitesListWidget.item(index)
            item_widget = self.invitesListWidget.itemWidget(list_item)
            if item_widget.is_selected():
                selected.append(all_invites[index])

        return selected

    def _refresh_invites_list(self):
        self.invitesListWidget.clear()
        invites = self._groups_service.get_group_invites()
        for invite in invites:
            self._create_invite_item(invite)

    def _create_invite_item(self, invite):
        friend = self._get_friend(invite.friend_public_key)
        item = GroupInviteItem(self.invitesListWidget, invite.chat_name, friend.get_pixmap(), friend.name)
        item.subscribe_checked_event(self._item_selected)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(item.width(), item.height()))
        self.invitesListWidget.addItem(elem)
        self.invitesListWidget.setItemWidget(elem, item)

    def _item_selected(self):
        self._update_buttons_state()

    def _nick_changed(self):
        self._update_buttons_state()

    def _update_buttons_state(self):
        nick = self.nickLineEdit.text()
        selected_items = self._get_selected_invites()
        self.acceptPushButton.setEnabled(bool(nick) and len(selected_items))
        self.declinePushButton.setEnabled(len(selected_items) > 0)
