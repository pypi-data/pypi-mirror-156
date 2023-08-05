import PyQt5
import PyQt5.QtWidgets


class UserNameDialog(PyQt5.QtWidgets.QDialog):
    """Класс реализующий стартовый диалог с запросом логина и пароля пользователя."""

    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Hello!')
        self.setFixedSize(175, 93)

        self.label = PyQt5.QtWidgets.QLabel('Input user name:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = PyQt5.QtWidgets.QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.btn_ok = PyQt5.QtWidgets.QPushButton('Start', self)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = PyQt5.QtWidgets.QPushButton('Exit', self)
        self.btn_cancel.move(90, 60)
        self.btn_cancel.clicked.connect(PyQt5.QtWidgets.qApp.exit)

        self.label_passwd = PyQt5.QtWidgets.QLabel('Enter password:', self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(150, 15)

        self.client_passwd = PyQt5.QtWidgets.QLineEdit(self)
        self.client_passwd.setFixedSize(154, 20)
        self.client_passwd.move(10, 75)
        self.client_passwd.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)

        self.show()

    def click(self):

        """Метод обрабтчик кнопки ОК."""
        if self.client_name.text() and self.client_passwd.text():
            self.ok_pressed = True
            PyQt5.QtWidgets.qApp.exit()


if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication([])
    dial = UserNameDialog()
    app.exec_()
