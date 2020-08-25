import unittest
from pathlib import Path
from unittest import mock
from api.theqoo import Theqoo

TEST_FILE_DIR = 'file'
path = Path(TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)
FILE_GARBAGE = f'{TEST_FILE_DIR}/garbage_session'


class GeneralTestCase(unittest.TestCase):
    testId = 'id'
    testPw = 'pw'

    def test_initialize(self):
        tq = Theqoo(self.testId, self.testPw)
        self.assertEqual(self.testId, tq.get_theqoo_id(), 'Login ID should be set after init')
        self.assertEqual(self.testPw, tq.get_theqoo_pw(), 'Login PW should be set after init')
        self.assertFalse(tq.is_logged_in(), 'Login flag should be False after just init')
        self.assertTrue(tq.has_session(), 'Should have session instance after init')

    def test_initialize_with_session_file(self):
        tq = Theqoo(self.testId, self.testPw, session_file_path=FILE_GARBAGE)
        self.assertEqual(self.testId, tq.get_theqoo_id(), 'Login ID should be set after init')
        self.assertEqual(self.testPw, tq.get_theqoo_pw(), 'Login PW should be set after init')
        self.assertFalse(tq.is_logged_in(), 'Login flag should be False after just init')
        self.assertTrue(tq.has_session(), 'Should have session instance after init')

    def test_when_theqoo_pw_not_set(self):
        # When Value is ''
        with self.assertRaises(ValueError):
            Theqoo(self.testId, '', no_directly_login=True)
        # When Value Is None
        with self.assertRaises(ValueError):
            Theqoo(self.testId, None)

    def test_when_theqoo_id_not_set(self):
        # When Value is ''
        with self.assertRaises(ValueError):
            Theqoo('', self.testPw, no_directly_login=True)
        # When Value Is None
        with self.assertRaises(ValueError):
            Theqoo(None, self.testPw)


if __name__ == '__main__':
    # suite = unittest.TestSuite()
    unittest.main()
