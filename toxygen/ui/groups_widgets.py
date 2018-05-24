from PyQt5 import uic
import utils.util as util
from ui.widgets import *
from wrapper.toxcore_enums_and_consts import *


class CreateGroupScreen(CenteredWidget):

    def __init__(self, groups_service):
        super().__init__()
        self._groups_service = groups_service
        uic.loadUi(util.get_views_path('create_group_screen'), self)
        self.center()
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()
        self.addGroupButton.clicked.connect(self._create_group)
        self.groupNameLineEdit.textChanged.connect(self._group_name_changed)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Create new group chat'))
        self.groupNameLabel.setText(util_ui.tr('Group name:'))
        self.groupTypeLabel.setText(util_ui.tr('Group type:'))
        self.groupNameLineEdit.setPlaceholderText(util_ui.tr('Group\'s persistent name'))
        self.addGroupButton.setText(util_ui.tr('Create group'))
        self.groupTypeComboBox.addItem(util_ui.tr('Public'))
        self.groupTypeComboBox.addItem(util_ui.tr('Private'))

    def _create_group(self):
        name = self.groupNameLineEdit.text()
        privacy_state = self.groupTypeComboBox.currentIndex()
        self._groups_service.create_new_gc(name, privacy_state)
        self.close()

    def _group_name_changed(self):
        name = self.groupNameLineEdit.text()
        self.addGroupButton.setEnabled(bool(name.strip()))


class JoinGroupScreen(CenteredWidget):

    def __init__(self, groups_service):
        super().__init__()
        self._groups_service = groups_service
        uic.loadUi(util.get_views_path('join_group_screen'), self)
        self.center()

    def _update_ui(self):
        self._retranslate_ui()
        self.chatIdLineEdit.textChanged.connect(self._chat_id_changed)
        self.joinGroupButton.clicked.connect(self._join_group)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Join public group chat'))
        self.chatIdLabel.setText(util_ui.tr('Group ID:'))
        self.passwordLabel.setText(util_ui.tr('Password:'))
        self.chatIdLineEdit.setPlaceholderText(util_ui.tr('Group\'s chat ID'))
        self.joinGroupButton.setText(util_ui.tr('Join group'))
        self.passwordLineEdit.setPlaceholderText(util_ui.tr('Optional password'))

    def _chat_id_changed(self):
        chat_id = self._get_chat_id()
        self.joinGroupButton.setEnabled(len(chat_id) == TOX_GROUP_CHAT_ID_SIZE * 2)

    def _join_group(self):
        chat_id = self._get_chat_id()
        password = self.passwordLineEdit.text()
        self._groups_service.join_gc_by_id(chat_id, password)
        self.close()

    def _get_chat_id(self):
        chat_id = self.chatIdLineEdit.text().strip()
        if chat_id.startswith('tox:'):
            chat_id = chat_id[4:]

        return chat_id
