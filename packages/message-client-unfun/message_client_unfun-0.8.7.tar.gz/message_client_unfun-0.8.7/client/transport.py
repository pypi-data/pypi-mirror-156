import socket
import time
import threading
import PyQt5.QtCore
from project.client_dist.common.utils import *
from project.client_dist.common.variables import *
from project.client_dist.logs.client_log_config import logger
import hashlib
import hmac
import binascii

socket_lock = threading.Lock()


class ClientTransport(threading.Thread, PyQt5.QtCore.QObject):
    """ ласс реализующий транспортную подсистему клиентского модул€. ќтвечает за взаимодействие с сервером."""

    new_message = PyQt5.QtCore.pyqtSignal(dict)
    message_205 = PyQt5.QtCore.pyqtSignal()
    connection_lost = PyQt5.QtCore.pyqtSignal()

    def __init__(self, port, ip_address, base, username, passwd, keys):
        threading.Thread.__init__(self)
        PyQt5.QtCore.QObject.__init__(self)
        self.base = base
        self.username = username
        self.password = passwd
        self.keys = keys
        self.client_sock = None
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                logger.critical(f'connection to the server is lost')
                raise ValueError('connection to the server is lost')
            logger.error('Connection timeout when updating user lists.')
        except json.JSONDecodeError:
            logger.critical(f'connection to the server is lost')
            raise ValueError('connection to the server is lost')
        self.running = True

    def connection_init(self, port, ip):
        """ћетод отвечающий за устанновку соединени€ с сервером."""

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_sock.settimeout(5)

        connected = False
        for i in range(5):
            logger.info(f'Connection attempt {i + 1}')
            try:
                self.client_sock.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                logger.debug("Connection established.")
                break
            time.sleep(1)

        if not connected:
            logger.critical('Failed to establish a connection to the server')
            raise ValueError('Failed to establish a connection to the server')

        logger.debug('Starting auth dialog.')

        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)

        logger.debug(f'Passwd hash ready: {passwd_hash_string}')

        pubkey = self.keys.publickey().export_key().decode('ascii')

        with socket_lock:
            presense = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            logger.debug(f"Presense message = {presense}")
            try:
                do_encode(self.client_sock, presense)
                ans = do_decode(self.client_sock)
                logger.debug(f'Server response = {ans}.')
                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ValueError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        ans_data = ans[DATA]
                        hash = hmac.new(passwd_hash_string, ans_data.encode('utf-8'), 'P4el')
                        digest = hash.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(
                            digest).decode('ascii')
                        do_encode(self.client_sock, my_ans)
                        self.process_server_ans(do_decode(self.client_sock))
            except (OSError, json.JSONDecodeError) as err:
                logger.debug(f'Connection error.', exc_info=err)
                raise ValueError('Connection failure during authorization.')

    def process_server_ans(self, message):
        """ћетод обработчик поступающих сообщений с сервера."""

        logger.debug(f'Parsing a message from the server: {message}')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ValueError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
            else:
                logger.debug(f'Unknown confirmation code received {message[RESPONSE]}')

        elif ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message and message[DESTINATION] == self.username:
            logger.debug(f'Received a message from the user {message[SENDER]}:{message[MESSAGE_TEXT]}')
            self.new_message.emit(message)

    def contacts_list_update(self):
        """ћетод обновл€ющий с сервера список контактов."""

        logger.debug(f'Request a contact sheet for the user {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        logger.debug(f'A request has been formed {req}')
        with socket_lock:
            do_encode(self.client_sock, req)
            ans = do_decode(self.client_sock)
        logger.debug(f'Response received {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.base.add_contact(contact)
        else:
            logger.error('Failed to update contact list.')

    def user_list_update(self):
        """ћетод обновл€ющий с сервера список пользователей."""

        logger.debug(f'Requesting a list of known users {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            do_encode(self.client_sock, req)
            ans = do_decode(self.client_sock)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.base.add_users(ans[LIST_INFO])
        else:
            logger.error('Failed to update the list of known users.')

    def key_request(self, user):
        """ћетод запрашивающий с сервера публичный ключ пользовател€."""

        logger.debug(f'Requesting a public key for {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            do_encode(self.client_sock, req)
            ans = do_decode(self.client_sock)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            logger.error(f'Could not get the interlocutor is key{user}.')

    def add_contact(self, contact):
        """ћетод отправл€ющий на сервер сведени€ о добавлении контакта."""

        logger.debug(f'Add contact {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            do_encode(self.client_sock, req)
            self.process_server_ans(do_decode(self.client_sock))

    def remove_contact(self, contact):
        """ћетод отправл€ющий на сервер сведени€ о удалении контакта."""

        logger.debug(f'Delete contact {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            do_encode(self.client_sock, req)
            self.process_server_ans(do_decode(self.client_sock))

    def transport_shutdown(self):
        """ћетод уведомл€ющий сервер о завершении работы клиента."""
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                do_encode(self.client_sock, message)
            except OSError:
                pass
        logger.debug('Transport is shutting down.')
        time.sleep(0.5)

    def send_message(self, to, message):
        """ћетод отправл€ющий на сервер сообщени€ дл€ пользовател€."""

        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'The message dictionary has been formed: {message_dict}')

        with socket_lock:
            do_encode(self.client_sock, message_dict)
            self.process_server_ans(do_decode(self.client_sock))
            logger.info(f'A message has been sent to the user {to}')

    def run(self):
        """ћетод содержащий основной цикл работы транспортного потока."""

        logger.debug('The process - receiver of messages from the server is started.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.client_sock.settimeout(0.5)
                    message = do_decode(self.client_sock)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'The connection to the server is lost.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.debug(f'The connection to the server is lost..')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'Received a message from the server: {message}')
                    self.process_server_ans(message)
                finally:
                    self.client_sock.settimeout(5)
