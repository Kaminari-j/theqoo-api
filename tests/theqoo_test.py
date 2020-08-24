import unittest
from api.theqoo import Theqoo
import requests
import ini

TEST_FILE_DIR = './file'
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
    testId = 'id'
    testPw = 'pw'

    def test_login_ok(self):
        tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, no_directly_login=True)
        tq.do_login(FILE_WITH_SESSION)
        self.assertTrue(tq.is_logged_in())

    def test_login_failed_with_id(self):
        tq = Theqoo(self.testId, ini.THEQOO_PW, no_directly_login=True)
        with self.assertRaises(ConnectionError):
            tq.do_login(FILE_NO_SESSION)

    def test_login_failed_with_pw(self):
        tq = Theqoo(ini.THEQOO_ID, self.testPw, no_directly_login=True)
        with self.assertRaises(ConnectionError):
            tq.do_login(FILE_NO_SESSION)

    def test_delete_comment_success(self):
        tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, no_directly_login=True)
        tq.do_login(FILE_WITH_SESSION)
        result = tq.delete_comment(1580192797)
        self.assertIsInstance(result, str)

    def test_delete_comment_fail(self):
        fail = Theqoo('testid', 'testpw', no_directly_login=True)
        # Not Logged In
        with self.assertRaises(RuntimeError):
            fail.delete_comment(1580192797)

    def test_get_user_comments_success(self):
        tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, no_directly_login=True)
        result = tq.get_user_comments()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for comment in result:
            self.assertRegex(comment, '[0-9]+')


class SessionTestCase(unittest.TestCase):
    tq = None

    @classmethod
    def setUpClass(cls) -> None:
        import os
        if not os.path.exists(FILE_WITH_SESSION):
            cls.tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW, FILE_WITH_SESSION)
        if not os.path.exists(FILE_NO_SESSION):
            try:
                cls.tq = Theqoo('nouser', 'nouser', FILE_NO_SESSION)
            except ConnectionError:
                pass

    def test_get_former_session_got_session(self):
        res = Theqoo.get_former_session(FILE_WITH_SESSION)
        self.assertIsNotNone(res)
        self.assertIsInstance(res, requests.Session)

    def test_get_former_session_no_session(self):
        res = Theqoo.get_former_session(FILE_NO_SESSION)
        self.assertIsNone(res)


if __name__ == '__main__':
    # suite = unittest.TestSuite()
    unittest.main()
