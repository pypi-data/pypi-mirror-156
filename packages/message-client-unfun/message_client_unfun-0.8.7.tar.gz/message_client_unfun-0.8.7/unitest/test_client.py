import sys
import os
from project.common.utils import message_presence, check_answer
from project.common.variables import *
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestClient(unittest.TestCase):

    def test_def_presence(self):
        test = message_presence()
        test[TIME] = 5.0
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 5.0, USER: {ACCOUNT_NAME: 'Vladimir'}})

    def test_name(self):
        self.assertFalse(ACCOUNT_NAME.isupper())
        self.assertTrue(ACCOUNT_NAME.title())
        self.assertTrue(ACCOUNT_NAME.islower())
        self.assertFalse(ACCOUNT_NAME.isdigit())

    def test_check_answer_200(self):
        self.assertEqual(check_answer({RESPONSE: 200}), '200 : OK')

    def test_check_answer_400(self):
        self.assertEqual(check_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, check_answer, ({ERROR: ['Bad Request']}))


if __name__ == '__main__':
    unittest.main()
