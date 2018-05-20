from ui.widgets import *
from wrapper.toxcore_enums_and_consts import *


class PeerItem(QtWidgets.QWidget):

    def __init__(self, peer, handler, width, parent=None):
        super().__init__(parent)
        self.resize(QtCore.QSize(width, 34))
        self.nameLabel = DataLabel(self)
        self.nameLabel.setGeometry(5, 0, width - 5, 34)
        name = peer.name
        if peer.is_current_user:
            name += util_ui.tr(' (You)')
        self.nameLabel.setText(name)
        if peer.status == TOX_USER_STATUS['NONE']:
            style = 'QLabel {color: green}'
        elif peer.status == TOX_USER_STATUS['AWAY']:
            style = 'QLabel {color: yellow}'
        else:
            style = 'QLabel {color: red}'
        self.nameLabel.setStyleSheet(style)
        self.nameLabel.mousePressEvent = lambda x: handler(peer.id)


class PeerTypeItem(QtWidgets.QWidget):

    def __init__(self, text, width, parent=None):
        super().__init__(parent)
        self.resize(QtCore.QSize(width, 34))
        self.nameLabel = DataLabel(self)
        self.nameLabel.setGeometry(5, 0, width - 5, 34)
        self.nameLabel.setText(text)
