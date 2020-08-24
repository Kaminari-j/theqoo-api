import unittest
from unittest.mock import MagicMock
import requests
from api import util


class UtilTestCase(unittest.TestCase):
    testfile_path = 'file/session'

    def test_save_session_to_file(self):
        session = requests.session()

        result = util.save_session(self.testfile_path, session)
        self.assertIsInstance(result, bool, 'Type of return value of function should be bool')
        self.assertTrue(result)

    def test_save_session_to_file_fail(self):
        result = util.save_session('dir_not_exists/session', None)
        self.assertIsInstance(result, bool, 'Type of return value of function should be bool')
        self.assertFalse(result)

    def test_load_session_from_file(self):
        s = util.load_session(self.testfile_path)
        self.assertIsNotNone(s)
        self.assertIsInstance(s, requests.Session)

    def test_load_session_from_file_fail(self):
        s = util.load_session('dir_not_exists/session.txt')
        self.assertIsNone(s)


if __name__ == '__main__':
    unittest.main()
