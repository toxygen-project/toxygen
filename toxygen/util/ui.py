import PyQt5


def tr(s):
    return PyQt5.QtWidgets.QApplication.translate('Toxygen', s)


def question(text):
    reply = PyQt5.QtWidgets.QMessageBox.question(None, 'Toxygen', text,
                                                 PyQt5.QtWidgets.QMessageBox.Yes,
                                                 PyQt5.QtWidgets.QMessageBox.No)
    return reply == PyQt5.QtWidgets.QMessageBox.Yes

# TODO: move all dialogs here
