import PyQt5.QtWidgets
from PyQt5.QtCore import Qt
import PyQt5.QtCore

from project.client_dist.logs.client_log_config import logger


class AddContactDialog(PyQt5.QtWidgets.QDialog):
    """Диалог добавления пользователя в список контактов.Предлагает пользователю список возможных контактов и добавляет
     выбранный в контакты."""

    def __init__(self, client_sock, base):
        super().__init__()
        self.client_sock = client_sock
        self.base = base
        self.setFixedSize(350, 120)
        self.setWindowTitle('Select a contact to add:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.selector_label = PyQt5.QtWidgets.QLabel('Select a contact to add:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)
        self.selector = PyQt5.QtWidgets.QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)
        self.btn_refresh = PyQt5.QtWidgets.QPushButton('Update the list', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)
        self.btn_ok = PyQt5.QtWidgets.QPushButton('Add', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_cancel = PyQt5.QtWidgets.QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)
        self.possible_contacts_update()
        self.btn_refresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        """Метод заполнения списка возможных контактов.Создаёт список всех зарегистрированных пользователей за
        исключением уже добавленных в контакты и самого себя."""

        self.selector.clear()
        contacts_list = set(self.base.get_contacts())
        users_list = set(self.base.get_users())
        users_list.remove(self.client_sock.username)
        self.selector.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        """Метод обновления списка возможных контактов. Запрашивает с сервера список известных пользователей и
        обносляет содержимое окна."""

        try:
            self.client_sock.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('Updating the list of users from the server has been completed')
            self.possible_contacts_update()
