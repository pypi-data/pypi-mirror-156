from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import hashlib
import binascii


class RegisterUser(QDialog):
    """ ����� ������ ����������� ������������ �� �������. """

    def __init__(self, base, server):
        super().__init__()

        self.base = base
        self.server = server

        self.setWindowTitle('Registration')
        self.setFixedSize(175, 183)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.label_username = QLabel('Input username:', self)
        self.label_username.move(10, 10)
        self.label_username.setFixedSize(150, 15)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.label_passwd = QLabel('Input password:', self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(150, 15)

        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(154, 20)
        self.client_passwd.move(10, 75)
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.label_conf = QLabel('Enter confirmation:', self)
        self.label_conf.move(10, 100)
        self.label_conf.setFixedSize(150, 15)

        self.client_conf = QLineEdit(self)
        self.client_conf.setFixedSize(154, 20)
        self.client_conf.move(10, 120)
        self.client_conf.setEchoMode(QLineEdit.Password)

        self.btn_ok = QPushButton('Save', self)
        self.btn_ok.move(10, 150)
        self.btn_ok.clicked.connect(self.save_data)

        self.btn_cancel = QPushButton('Exit', self)
        self.btn_cancel.move(90, 150)
        self.btn_cancel.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.show()

    def save_data(self):
        """ ����� �������� ������������ ����� � ���������� � ���� ������ ������������."""

        if not self.client_name.text():
            self.messages.critical(
                self, 'Error', 'User name not specified.')
            return
        elif self.client_passwd.text() != self.client_conf.text():
            self.messages.critical(
                self, 'Error', 'The entered passwords do not match.')
            return
        elif self.base.check_user(self.client_name.text()):
            self.messages.critical(
                self, 'Error', 'The user already exists.')
            return
        else:
            passwd_bytes = self.client_passwd.text().encode('utf-8')
            salt = self.client_name.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac(
                'sha512', passwd_bytes, salt, 10000)
            self.base.add_user(
                self.client_name.text(),
                binascii.hexlify(passwd_hash))
            self.messages.information(
                self, 'Success', 'User successfully registered.')

            self.server.service_update_lists()
            self.close()


if __name__ == '__main__':
    app = QApplication([])
    from my_server_base import ServerDB
    base = ServerDB('../my_server_base.db3')
    import os
    import sys
    path1 = os.path.join(os.getcwd(), '..')
    sys.path.insert(0, path1)
    from core import MessageProcessor
    server = MessageProcessor('127.0.0.1', 7777, base)
    dial = RegisterUser(base, server)
    app.exec_()
