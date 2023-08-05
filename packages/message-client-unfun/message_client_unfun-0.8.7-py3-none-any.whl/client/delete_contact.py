import PyQt5.QtWidgets
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger('client')


class DelContactDialog(PyQt5.QtWidgets.QDialog):
    """Диалог удаления контакта. Предлагает текущий список контактов,не имеет обработчиков для действий.
    """
    def __init__(self, base):
        super().__init__()
        self.base = base

        self.setFixedSize(350, 120)
        self.setWindowTitle('Select the contact to delete:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.selector_label = PyQt5.QtWidgets.QLabel('Select the contact to delete:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = PyQt5.QtWidgets.QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)
        self.selector.addItems(sorted(self.base.get_contacts()))

        self.btn_ok = PyQt5.QtWidgets.QPushButton('Delete', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = PyQt5.QtWidgets.QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)


if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication([])
    window = DelContactDialog(None)
    window.show()
    app.exec_()
