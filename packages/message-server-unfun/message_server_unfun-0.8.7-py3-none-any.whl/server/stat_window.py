from PyQt5.QtWidgets import QDialog, QPushButton, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


class StatWindow(QDialog):
    """Класс - окно со статистикой пользователей"""
    def __init__(self, base):
        super().__init__()

        self.base = base
        self.initUI()

    def initUI(self):

        self.setWindowTitle('Clients statistic')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)
        self.stat_table = QTableView(self)
        self.stat_table.move(10, 10)
        self.stat_table.setFixedSize(580, 620)

        self.create_stat_model()

    def create_stat_model(self):
        """Метод реализующий заполнение таблицы статистикой сообщений."""

        stat_list = self.base.message_history()

        lst = QStandardItemModel()
        lst.setHorizontalHeaderLabels(
            ['Client Name', 'Last logged in', 'Messages sent', 'Messages Received'])
        for row in stat_list:
            user, last_seen, sent, recvd = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            recvd = QStandardItem(str(recvd))
            recvd.setEditable(False)
            lst.appendRow([user, last_seen, sent, recvd])
        self.stat_table.setModel(lst)
        self.stat_table.resizeColumnsToContents()
        self.stat_table.resizeRowsToContents()
