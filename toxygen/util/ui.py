from PyQt5 import QtWidgets


def tr(s):
    return QtWidgets.QApplication.translate('Toxygen', s)


def question(text, title=None):
    reply = QtWidgets.QMessageBox.question(None, title or 'Toxygen', text,
                                           QtWidgets.QMessageBox.Yes,
                                           QtWidgets.QMessageBox.No)
    return reply == QtWidgets.QMessageBox.Yes


def message_box(text, title=None):
    m_box = QtWidgets.QMessageBox()
    m_box.setText(tr(text))
    m_box.setWindowTitle(title or 'Toxygen')
    m_box.exec_()


def text_dialog(text, title='', default_value=''):
    text, ok = QtWidgets.QInputDialog.getText(None, title, text, QtWidgets.QLineEdit.Normal, default_value)

    return text, ok


# TODO: move all dialogs here
