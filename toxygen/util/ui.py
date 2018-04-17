import PyQt5


def tr(s):
    return PyQt5.QtWidgets.QApplication.translate('Toxygen', s)


def question(text, title=None):
    reply = PyQt5.QtWidgets.QMessageBox.question(None, title or 'Toxygen', text,
                                                 PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.No)
    return reply == PyQt5.QtWidgets.QMessageBox.Yes


def message_box(text, title=None):
    m_box = PyQt5.QtWidgets.QMessageBox()
    m_box.setText(tr(text))
    m_box.setWindowTitle(title or 'Toxygen')
    m_box.exec_()

# TODO: move all dialogs here
