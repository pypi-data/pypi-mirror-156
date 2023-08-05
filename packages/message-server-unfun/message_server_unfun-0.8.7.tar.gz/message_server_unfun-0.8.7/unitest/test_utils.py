from project.common.variables import *
import unittest
from project.common.utils import do_encode, do_decode
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestSocket:

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message_to_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.received_message = message_to_send

    def data_from_socket(self):

        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):

    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 5.0,
        USER: {
            ACCOUNT_NAME: 'Vladimir'
        }
    }

    def test_encode_true(self):

        test_socket = TestSocket(self.test_dict_send)
        do_encode(self.test_dict_send, test_socket)
        self.assertEqual(test_socket.encoded_message, test_socket.received_message)

    def test_encode_error(self):
        test_socket = TestSocket(self.test_dict_send)
        do_encode(self.test_dict_send, test_socket)
        self.assertRaises(TypeError, do_encode, test_socket, "undict")

    def test_decode(self):
        self.assertRaises(ValueError, do_decode, self.test_dict_send)


if __name__ == '__main__':
    unittest.main()

