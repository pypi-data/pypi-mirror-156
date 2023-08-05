from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker
import datetime


class ServerDB:
    """ ����� - �������� ��� ������ � ����� ������ �������. ���������� SQLite ���� ������, ���������� � �������
        SQLAlchemy ORM � ������������ ������������ ������."""

    class AllUsers:
        """����� - ����������� ������� ���� �������������."""

        def __init__(self, username, passwd_hash):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

    class ActiveUsers:
        """����� - ����������� ������� �������� �������������."""

        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        """����� - ����������� ������� ������� ������."""

        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    class UsersContacts:
        """����� - ����������� ������� ��������� �������������."""

        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    class UsersHistory:
        """����� - ����������� ������� ������� ��������."""

        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        self.base_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                         connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        users = Table('Users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String, unique=True),
                      Column('last_login', DateTime),
                      Column('passwd_hash', String),
                      Column('pubkey', Text)
                      )

        active_users = Table('Active_users', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('user', ForeignKey('Users.id'), unique=True),
                             Column('ip_address', String),
                             Column('port', Integer),
                             Column('login_time', DateTime)
                             )

        user_history = Table('User_history', self.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('name', ForeignKey('Users.id')),
                             Column('date_time', DateTime),
                             Column('ip', String),
                             Column('port', String)
                             )
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        history_for_users = Table('History', self.metadata,
                                  Column('id', Integer, primary_key=True),
                                  Column('user', ForeignKey('Users.id')),
                                  Column('sent', Integer),
                                  Column('accepted', Integer)
                                  )

        self.metadata.create_all(self.base_engine)
        mapper(self.AllUsers, users)
        mapper(self.ActiveUsers, active_users)
        mapper(self.LoginHistory, user_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, history_for_users)

        user_session = sessionmaker(bind=self.base_engine)
        self.session = user_session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port, key):
        """����� ������������� ��� ����� ������������, ���������� � ���� ���� �����
        ��������� �������� ���� ������������ ��� ��� ���������."""

        print(username, ip_address, port)
        res = self.session.query(self.AllUsers).filter_by(name=username)

        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError('The user is not registered.')

        new_user_active = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_user_active)
        history_user = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history_user)
        self.session.commit()

    def add_user(self, name, passwd_hash):
        """����� ����������� ������������.��������� ��� � ��� ������, ������ ������ � ������� ����������."""

        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """����� ��������� ������������ �� ����."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(
            self.UsersContacts).filter_by(
            contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """����� ��������� ���� ������ ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """����� ��������� ���������� ����� ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        """����� ����������� ������������� ������������."""

        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_exit(self, username):
        """����� ����������� ���������� ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        """����� ������������ � ������� ���������� ���� �������� ���������."""

        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        """����� ���������� �������� ��� ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """����� �������� �������� ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()

        if not contact:
            return

        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    def users_list(self):
        """����� ������������ ������ ��������� ������������� �� �������� ���������� �����."""

        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    def active_users_list(self):
        """����� ������������ ������ �������� �������������."""

        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def user_login_history(self, username=None):
        """����� ������������ ������� ������."""
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    def get_contacts(self, username):
        """����� ������������ ������ ��������� ������������."""

        user = self.session.query(self.AllUsers).filter_by(name=username).one()
        query = self.session.query(self.UsersContacts, self.AllUsers.name).filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        return [contact[1] for contact in query.all()]

    def message_history(self):
        """����� ������������ ���������� ���������."""

        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)

        return query.all()


if __name__ == '__main__':
    db = ServerDB('my_server_base.db3')
    db.user_login('client_first', '192.168.88.1', 8888)
    db.user_login('client_second', '192.168.88.2', 7777)
    print(db.users_list())
    # pprint(db.active_users_list())
    # db.user_exit('client_first')
    # pprint(db.user_login_history('client_first'))
    # db.add_contact('user2', 'user1')
    # db.add_contact('user1', 'user3')
    # db.add_contact('user1', 'user6')
    # db.remove_contact('user1', 'user3')
    db.process_message('client_second', 'client_first')
    print(db.message_history())



