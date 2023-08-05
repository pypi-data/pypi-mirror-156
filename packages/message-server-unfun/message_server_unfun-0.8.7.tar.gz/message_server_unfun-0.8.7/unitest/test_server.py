from project.common.utils import check_jim
from project.common.variables import *
import unittest
import os
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))


class TestServer(unittest.TestCase):
    good_result_dict = {RESPONSE: 200}
    bad_result_dict = {RESPONSE: 400,
                       ERROR: 'Bad Request'
    }

    def test_no_user(self):
        self.assertEqual(check_jim({ACTION: PRESENCE, TIME: 5.0}), self.bad_result_dict)

    def test_ok_result(self):
        self.assertEqual(check_jim({ACTION: PRESENCE, TIME: 5.0, USER: {ACCOUNT_NAME: 'Vladimir'}}), self.good_result_dict)

    def test_no_time_and_dif_user(self):
        self.assertEqual(check_jim({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Ivan'}}), self.bad_result_dict)

    def test_without_action(self):
        self.assertEqual(check_jim({TIME: 5.0, USER: {ACCOUNT_NAME: 'Vladimir'}}), self.bad_result_dict)
