import json
from project.server_dist.common.variables import *
from project.server_dist.common.decorator import log
import sys
sys.path.append('../')


@log
def do_encode(sock, message):
    """������� �������� �������� ����� �����.
    �������� ������� � ������ JSON � ���������� ����� �����.
    :param sock: ����� ��� ��������
    :param message: ������� ��� ��������
    :return: ������ �� ����������"""

    if not isinstance(message, dict):
        raise TypeError
    query = json.dumps(message).encode(ENCODING)
    sock.send(query)


@log
def do_decode(client):
    """������� ����� ��������� �� �������� �����������.��������� ��������� JSON, ���������� ���������� ���������
    � ��������� ��� ������� �������.:param client: ����� ��� �������� ������.
    :return: ������� - ���������."""

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError
