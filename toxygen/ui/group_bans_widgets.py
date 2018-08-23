from ui.widgets import CenteredWidget
from PyQt5 import uic, QtWidgets, QtCore
import utils.util as util
import utils.ui as util_ui


class GroupBanItem(QtWidgets.QWidget):

    def __init__(self, ban, cancel_ban, can_cancel_ban, parent=None):
        super().__init__(parent)
        self._ban = ban
        self._cancel_ban = cancel_ban
        self._can_cancel_ban = can_cancel_ban

        uic.loadUi(util.get_views_path('gc_ban_item'), self)
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self.banTargetLabel.setText(self._ban.ban_target)
        ban_time = self._ban.ban_time
        self.banTimeLabel.setText(util.unix_time_to_long_str(ban_time))

        self.cancelPushButton.clicked.connect(self._cancel_ban)
        self.cancelPushButton.setEnabled(self._can_cancel_ban)

    def _retranslate_ui(self):
        self.cancelPushButton.setText(util_ui.tr('Cancel ban'))

    def _cancel_ban(self):
        self._cancel_ban(self._ban.ban_id)


class GroupBansScreen(CenteredWidget):

    def __init__(self, groups_service, group):
        super().__init__()
        self._groups_service = groups_service
        self._group = group

        uic.loadUi(util.get_views_path('bans_list_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self._refresh_bans_list()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Bans list for group "{}"').format(self._group.name))

    def _refresh_bans_list(self):
        self.bansListWidget.clear()
        can_cancel_ban = self._group.is_self_moderator_or_founder()
        for ban in self._group.bans:
            self._create_ban_item(ban, can_cancel_ban)

    def _create_ban_item(self, ban, can_cancel_ban):
        item = GroupBanItem(ban, self._on_ban_cancelled, can_cancel_ban, self.bansListWidget)
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(item.width(), item.height()))
        self.bansListWidget.addItem(elem)
        self.bansListWidget.setItemWidget(elem, item)

    def _on_ban_cancelled(self, ban_id):
        self._groups_service.cancel_ban(self._group.number, ban_id)
        self._refresh_bans_list()
