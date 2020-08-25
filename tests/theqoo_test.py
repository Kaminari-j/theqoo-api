import unittest
from pathlib import Path
from api.theqoo import Theqoo
import requests
import ini

TEST_FILE_DIR = './file'
path = Path(TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)
FILE_WITH_SESSION = f'{TEST_FILE_DIR}/with_session'
FILE_NO_SESSION = f'{TEST_FILE_DIR}/no_session'


class GeneralTestCase(unittest.TestCase):
    testId = 'id'
    testPw = 'pw'

    def test_initialize(self):
        tq = Theqoo(self.testId, self.testPw)
        self.assertFalse(tq.is_logged_in(), 'Login flag should be False after just init')
        self.assertTrue(tq.has_session(), 'Should have session instance after init')
        self.assertEqual(self.testId, tq.get_theqoo_id())
        self.assertEqual(self.testPw, tq.get_theqoo_pw())

    def test_when_theqoo_pw_not_set(self):
        # When Value is ''
        with self.assertRaises(ValueError):
            Theqoo(self.testId, '')
        # When Value Is None
        with self.assertRaises(ValueError):
            Theqoo(self.testId, None)

    def test_when_theqoo_id_not_set(self):
        # When Value is ''
        with self.assertRaises(ValueError):
            Theqoo('', self.testPw)
        # When Value Is None
        with self.assertRaises(ValueError):
            Theqoo(None, self.testPw)


class LoginTestCase(unittest.TestCase):
    tq_normal = None

    testId = 'id'
    testPw = 'pw'

    @classmethod
    def setUpClass(cls) -> None:
        cls.tq_normal = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, FILE_WITH_SESSION, no_directly_login=True)
        print(f'Login Status : {"Logged In" if cls.tq_normal.is_logged_in() else "Not Logged In"}')

    def setUp(self) -> None:
        if not self.tq_normal.is_logged_in():
            self.tq_normal.do_login(FILE_WITH_SESSION)

    def test_login_ok(self):
        self.tq_normal.do_login(FILE_WITH_SESSION)
        self.assertTrue(self.tq_normal.is_logged_in())

    def test_login_failed_with_id(self):
        tq = Theqoo(self.testId, ini.THEQOO_PW, no_directly_login=True)
        with self.assertRaises(ConnectionError):
            tq.do_login(FILE_NO_SESSION)

    def test_login_failed_with_pw(self):
        tq = Theqoo(ini.THEQOO_ID, self.testPw, no_directly_login=True)
        with self.assertRaises(ConnectionError):
            tq.do_login(FILE_NO_SESSION)

    def test_delete_comment_success(self):
        result = self.tq_normal.delete_comment(1580192797)
        self.assertIsInstance(result, str)

    def test_delete_comment_fail(self):
        fail = Theqoo('testid', 'testpw', no_directly_login=True)
        # Not Logged In
        with self.assertRaises(RuntimeError):
            fail.delete_comment(1580192797)

    def test_get_user_comments_success(self):
        result = self.tq_normal.get_user_comments()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for comment in result:
            self.assertRegex(comment, '[0-9]+')


class SessionTestCase(unittest.TestCase):
    def test_get_former_session_got_session(self):
        Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, FILE_WITH_SESSION)
        res = Theqoo.get_former_session(FILE_WITH_SESSION)
        self.assertIsNotNone(res)
        self.assertIsInstance(res, requests.Session)

    def test_get_former_session_no_session(self):
        try:
            Theqoo('nouser', 'nouser', FILE_NO_SESSION)
        except ConnectionError:
            pass
        res = Theqoo.get_former_session(FILE_NO_SESSION)
        self.assertIsNone(res)


if __name__ == '__main__':
    # suite = unittest.TestSuite()
    unittest.main()
