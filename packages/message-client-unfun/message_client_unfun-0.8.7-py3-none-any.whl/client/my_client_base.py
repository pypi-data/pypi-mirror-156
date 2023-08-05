import datetime
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import os


class Clientbase:
    """ ласс - оболочка дл€ работы с базой данных клиента.»спользует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используетс€ классический подход."""

    class KnownUsers:
        """ ласс - отображение дл€ таблицы всех пользователей."""

        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageStat:
        """ ласс - отображение дл€ таблицы статистики переданных сообщений."""

        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        """ ласс - отображение дл€ таблицы контактов."""

        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):

        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.db3'
        self.base_engine = create_engine(
            f'sqlite:///{os.path.join(path, filename)}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False})

        self.metadata = MetaData()

        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )

        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('contact', String),
                        Column('direction', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )

        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )

        self.metadata.create_all(self.base_engine)

        mapper(self.KnownUsers, users)
        mapper(self.MessageStat, history)
        mapper(self.Contacts, contacts)

        user_session = sessionmaker(bind=self.base_engine)
        self.session = user_session()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """ ћетод добавл€ющий контакт в базу данных. """

        if not self.session.query(
                self.Contacts).filter_by(
                name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        """ ћетод, удал€ющий определЄнный контакт. """

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def del_contact(self, contact):
        """ ћетод, удал€ющий определЄнный контакт. """

        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def add_users(self, users_list):
        """ ћетод, заполн€ющий таблицу известных пользователей. """

        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """ ћетод, сохран€ющий сообщение в базе данных. """

        message_row = self.MessageStat(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """ ћетод, возвращающий список всех контактов. """

        return [contact[0]
                for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """ ћетод возвращающий список всех известных пользователей. """

        return [user[0]
                for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """ ћетод, провер€ющий существует ли пользователь. """

        if self.session.query(
                self.KnownUsers).filter_by(
                username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """ ћетод, провер€ющий существует ли контакт. """

        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """ ћетод, возвращающий историю сообщений с определЄнным пользователем. """
        query = self.session.query(
            self.MessageStat).filter_by(
            contact=contact)
        return [(history_row.contact,
                 history_row.direction,
                 history_row.message,
                 history_row.date) for history_row in query.all()]


if __name__ == '__main__':
    test_db = Clientbase('user1')
    for i in ['user3', 'user4', 'user5']:
        test_db.add_contact(i)
    test_db.add_contact('user4')
    test_db.add_users(['user1', 'user2', 'user3', 'user4', 'user5'])
    test_db.save_message('user2', 'in', f'Hello! My friend {datetime.datetime.now()}!')
    test_db.save_message('user2', 'out', f'Hello! My dear friend {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('user1'))
    print(test_db.check_user('user10'))
    print(sorted(test_db.get_history('user2'), key=lambda item: item[3]))
    test_db.del_contact('user4')
    print(test_db.get_contacts())
