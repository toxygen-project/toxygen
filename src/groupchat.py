import contact


class Groupchat(contact.Contact):

    def __init__(self, *args):
        super().__init__(args)

    def load_avatar(self):
        avatar_path = curr_directory() + '/images/group.png'
        os.chdir(curr_directory() + '/images/')
        pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
        pixmap.load(avatar_path)
        self._widget.avatar_label.setScaledContents(False)
        self._widget.avatar_label.setPixmap(pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))
        self._widget.avatar_label.repaint()
