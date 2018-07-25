from PyQt5 import uic
import utils.util as util
from ui.widgets import *
from wrapper.toxcore_enums_and_consts import *

# TODO: move common logic to separate class


class CreateGroupScreen(CenteredWidget):

    def __init__(self, groups_service, profile):
        super().__init__()
        self._groups_service = groups_service
        self._profile = profile
        uic.loadUi(util.get_views_path('create_group_screen'), self)
        self.center()
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self.statusComboBox.setCurrentIndex(self._profile.status or 0)
        self.nickLineEdit.setText(self._profile.name)

        self.addGroupButton.clicked.connect(self._create_group)
        self.groupNameLineEdit.textChanged.connect(self._group_name_changed)
        self.nickLineEdit.textChanged.connect(self._nick_changed)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Create new group chat'))
        self.groupNameLabel.setText(util_ui.tr('Group name:'))
        self.groupTypeLabel.setText(util_ui.tr('Group type:'))
        self.nickLabel.setText(util_ui.tr('Nickname:'))
        self.statusLabel.setText(util_ui.tr('Status:'))
        self.nickLineEdit.setPlaceholderText(util_ui.tr('Your nick in chat'))
        self.groupNameLineEdit.setPlaceholderText(util_ui.tr('Group\'s persistent name'))
        self.addGroupButton.setText(util_ui.tr('Create group'))
        self.groupTypeComboBox.addItem(util_ui.tr('Public'))
        self.groupTypeComboBox.addItem(util_ui.tr('Private'))
        self.groupTypeComboBox.setCurrentIndex(1)
        self.statusComboBox.addItem(util_ui.tr('Online'))
        self.statusComboBox.addItem(util_ui.tr('Away'))
        self.statusComboBox.addItem(util_ui.tr('Busy'))

    def _create_group(self):
        group_name = self.groupNameLineEdit.text()
        privacy_state = self.groupTypeComboBox.currentIndex()
        nick = self.nickLineEdit.text()
        status = self.statusComboBox.currentIndex()
        self._groups_service.create_new_gc(group_name, privacy_state, nick, status)
        self.close()

    def _nick_changed(self):
        self._update_button_state()

    def _group_name_changed(self):
        self._update_button_state()

    def _update_button_state(self):
        is_nick_set = bool(self.nickLineEdit.text())
        is_group_name_set = bool(self.groupNameLineEdit.text())
        self.addGroupButton.setEnabled(is_nick_set and is_group_name_set)


class JoinGroupScreen(CenteredWidget):

    def __init__(self, groups_service, profile):
        super().__init__()
        self._groups_service = groups_service
        self._profile = profile
        uic.loadUi(util.get_views_path('join_group_screen'), self)
        self.center()
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self.statusComboBox.setCurrentIndex(self._profile.status or 0)
        self.nickLineEdit.setText(self._profile.name)

        self.chatIdLineEdit.textChanged.connect(self._chat_id_changed)
        self.joinGroupButton.clicked.connect(self._join_group)
        self.nickLineEdit.textChanged.connect(self._nick_changed)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Join public group chat'))
        self.chatIdLabel.setText(util_ui.tr('Group ID:'))
        self.passwordLabel.setText(util_ui.tr('Password:'))
        self.nickLabel.setText(util_ui.tr('Nickname:'))
        self.statusLabel.setText(util_ui.tr('Status:'))
        self.chatIdLineEdit.setPlaceholderText(util_ui.tr('Group\'s chat ID'))
        self.nickLineEdit.setPlaceholderText(util_ui.tr('Your nick in chat'))
        self.joinGroupButton.setText(util_ui.tr('Join group'))
        self.passwordLineEdit.setPlaceholderText(util_ui.tr('Optional password'))
        self.statusComboBox.addItem(util_ui.tr('Online'))
        self.statusComboBox.addItem(util_ui.tr('Away'))
        self.statusComboBox.addItem(util_ui.tr('Busy'))

    def _chat_id_changed(self):
        self._update_button_state()

    def _nick_changed(self):
        self._update_button_state()

    def _update_button_state(self):
        chat_id = self._get_chat_id()
        is_nick_set = bool(self.nickLineEdit.text())
        self.joinGroupButton.setEnabled(len(chat_id) == TOX_GROUP_CHAT_ID_SIZE * 2 and is_nick_set)

    def _join_group(self):
        chat_id = self._get_chat_id()
        password = self.passwordLineEdit.text()
        nick = self.nickLineEdit.text()
        status = self.statusComboBox.currentIndex()
        self._groups_service.join_gc_by_id(chat_id, password, nick, status)
        self.close()

    def _get_chat_id(self):
        chat_id = self.chatIdLineEdit.text().strip()
        if chat_id.startswith('tox:'):
            chat_id = chat_id[4:]

        return chat_id
