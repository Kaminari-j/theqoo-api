import os
import unittest
from pathlib import Path
from unittest import mock
from api.theqoo import Theqoo
from tests import test_setting

path = Path(test_setting.TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)


class GeneralTestCase(unittest.TestCase):
    testId = 'id'
    testPw = 'pw'

    def tearDown(self) -> None:
        if os.path.exists(test_setting.FILE_GARBAGE):
            os.remove(test_setting.FILE_GARBAGE)

    def test_initialize(self):
        tq = Theqoo(self.testId, self.testPw)
        self.assertEqual(self.testId, tq.get_theqoo_id(), 'Login ID should be set after init')
        self.assertEqual(self.testPw, tq.get_theqoo_pw(), 'Login PW should be set after init')
        self.assertIsNotNone(tq.get_session_file_path())
        self.assertFalse(tq.is_logged_in(), 'Login flag should be False after just init')
        self.assertTrue(tq.has_session(), 'Should have session instance after init')

    def test_initialize_with_session_file(self):
        tq = Theqoo(self.testId, self.testPw, session_file_path=test_setting.FILE_GARBAGE)
        self.assertEqual(self.testId, tq.get_theqoo_id(), 'Login ID should be set after init')
        self.assertEqual(self.testPw, tq.get_theqoo_pw(), 'Login PW should be set after init')
        self.assertIsNotNone(tq.get_session_file_path())
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
