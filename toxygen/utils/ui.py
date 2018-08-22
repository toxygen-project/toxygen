from PyQt5 import QtWidgets
import utils.util as util


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


def directory_dialog(caption=''):
    return QtWidgets.QFileDialog.getExistingDirectory(None, caption, util.curr_directory(),
                                                      QtWidgets.QFileDialog.DontUseNativeDialog)


def file_dialog(caption, file_filter=None):
    return QtWidgets.QFileDialog.getOpenFileName(None, caption, util.curr_directory(), file_filter,
                                                 options=QtWidgets.QFileDialog.DontUseNativeDialog)


def save_file_dialog(caption, filter=None):
    return QtWidgets.QFileDialog.getSaveFileName(None, caption, util.curr_directory(),
                                                 filter=filter,
                                                 options=QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontUseNativeDialog)


def close_all_windows():
    QtWidgets.QApplication.closeAllWindows()


def copy_to_clipboard(text):
    clipboard = QtWidgets.QApplication.clipboard()
    clipboard.setText(text)


# TODO: all dialogs
