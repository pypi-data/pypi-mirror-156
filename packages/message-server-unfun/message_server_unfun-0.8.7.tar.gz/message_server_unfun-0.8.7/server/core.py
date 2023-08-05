import threading
import logging
import select
import socket
import hmac
import binascii
import os
from project.server_dist.common.descriptor import Port
from project.server_dist.common.utils import *
from project.server_dist.common.decorator import login_required


logger = logging.getLogger('server')


class MessageProcessor(threading.Thread):
    """Основной класс сервера. Принимает содинения, словари - пакеты от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока."""

    port = Port()

    def __init__(self, listen_address, listen_port, base):
        self.addr = listen_address
        self.port = listen_port
        self.base = base

        self.sock = None

        self.clients = []

        self.listen_sockets = None
        self.error_sockets = None

        self.running = True

        self.names = dict()

        super().__init__()

    def run(self):
        """Метод основной цикл потока."""

        self.init_socket()

        while self.running:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Connection with PC is established {client_address}')
                client.settimeout(5)
                self.clients.append(client)

            recv_data_lst = []
            try:
                if self.clients:
                    recv_data_lst, self.listen_sockets, self.error_sockets = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                logger.error(f'Error working with sockets: {err.errno}')

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(
                            do_decode(client_with_message), client_with_message)
                    except (OSError, json.JSONDecodeError, TypeError) as err:
                        logger.debug(f'Getting data from client exception.', exc_info=err)
                        self.remove_client(client_with_message)

    def remove_client(self, client):
        """Метод обработчик клиента с которым прервана связь.Ищет клиента и удаляет его из списков и базы:"""

        logger.info(f'Client {client.getpeername()} disconnected from the server.')
        for name in self.names:
            if self.names[name] == client:
                self.base.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def init_socket(self):
        """Метод инициализатор сокета."""

        logger.info(
            f' The server is running, the port for connections is: {self.port}, the address from which connections '
            f'are accepted is: {self.addr}.'f' If the address is not specified, connections from any '
            f'addresses are accepted.')

        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.addr, self.port))
        server_sock.settimeout(0.5)
        self.sock = server_sock
        self.sock.listen(MAX_CONNECTIONS)

    def process_message(self, message):
        """Метод отправки сообщения клиенту."""

        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in self.listen_sockets:
            try:
                do_encode(self.names[message[DESTINATION]], message)
                logger.info(
                    f'A message was sent to the user {message[DESTINATION]} from the user {message[SENDER]}.')
            except OSError:
                self.remove_client(message[DESTINATION])
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in self.listen_sockets:
            logger.error(
                f'Communication with the client {message[DESTINATION]} was lost. The connection is closed, '
                f'delivery is not possible.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            logger.error(
                f'The user {message[DESTINATION]} is not registered on the server, '
                f'sending the message is not possible.')

    @login_required
    def process_client_message(self, message, client):
        """ Метод обработчик поступающих сообщений. """

        logger.debug(f'Parsing a message from a client : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            self.autorization_user(message, client)

        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.base.process_message(
                    message[SENDER], message[DESTINATION])
                self.process_message(message)
                try:
                    do_encode(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'The user is not registered on the server.'
                try:
                    do_encode(client, response)
                except OSError:
                    pass
            return

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.remove_client(client)

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.base.get_contacts(message[USER])
            try:
                do_encode(client, response)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.base.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                do_encode(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.base.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                do_encode(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.base.users_list()]
            try:
                do_encode(client, response)
            except OSError:
                self.remove_client(client)

        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.base.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    do_encode(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'There is no public key for this user'
                try:
                    do_encode(client, response)
                except OSError:
                    self.remove_client(client)

        else:
            response = RESPONSE_400
            response[ERROR] = 'The request is incorrect.'
            try:
                do_encode(client, response)
            except OSError:
                self.remove_client(client)

    def autorization_user(self, message, sock):
        """ Метод реализующий авторизацию пользователей. """

        logger.debug(f'Start auth process for {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'The username is already taken.'
            try:
                logger.debug(f'Username busy, sending {response}')
                do_encode(sock, response)
            except OSError:
                logger.debug('OS Error')
                pass
            self.clients.remove(sock)
            sock.close()
        elif not self.base.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'The user is not registered.'
            try:
                logger.debug(f'Unknown username, sending {response}')
                do_encode(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            logger.debug('Correct username, starting passwd check.')
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_str.decode('ascii')
            hash = hmac.new(self.base.get_hash(message[USER][ACCOUNT_NAME]), random_str, 'P4el')
            digest = hash.digest()
            logger.debug(f'Auth message = {message_auth}')
            try:
                do_encode(sock, message_auth)
                ans = do_decode(sock)
            except OSError as err:
                logger.debug('Error in auth, data:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            if RESPONSE in ans and ans[RESPONSE] == 511 and \
                    hmac.compare_digest(digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    do_encode(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                self.base.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY])
            else:
                response = RESPONSE_400
                response[ERROR] = 'Invalid password.'
                try:
                    do_encode(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def service_update_lists(self):
        """Метод реализующий отправки сервисного сообщения 205 клиентам."""

        for client in self.names:
            try:
                do_encode(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
