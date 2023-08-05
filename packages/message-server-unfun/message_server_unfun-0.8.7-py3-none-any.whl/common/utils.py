import json
from project.server_dist.common.variables import *
from project.server_dist.common.decorator import log
import sys
sys.path.append('../')


@log
def do_encode(sock, message):
    """Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: сокет для передачи
    :param message: словарь для передачи
    :return: ничего не возвращает"""

    if not isinstance(message, dict):
        raise TypeError
    query = json.dumps(message).encode(ENCODING)
    sock.send(query)


@log
def do_decode(client):
    """Функция приёма сообщений от удалённых компьютеров.Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.:param client: сокет для передачи данных.
    :return: словарь - сообщение."""

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError
