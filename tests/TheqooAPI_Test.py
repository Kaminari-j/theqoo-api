import unittest
from eraser.Theqoo import Theqoo
from eraser import ini


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
        tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
        tq.login()
        self.assertTrue(tq.is_logged_in())

    def test_login_failed_with_id(self):
        tq = Theqoo(self.testId, ini.THEQOO_PW)
        with self.assertRaises(ConnectionError) as s:
            tq.login()

    def test_login_failed_with_pw(self):
        tq = Theqoo(ini.THEQOO_ID, self.testPw)
        with self.assertRaises(ConnectionError) as s:
            tq.login()


class DeleteCommentTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
        cls.tq.login()

    def test_delete_comment_success(self):
        result = self.tq.delete_comment(1580192797)
        self.assertIsInstance(result, str)

    def test_delete_comment_fail(self):
        failer = Theqoo('testid', 'testpw')
        # Not Logged In
        with self.assertRaises(RuntimeError):
            failer.delete_comment(1580192797)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tq = None


class GetUserComments(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
        cls.tq.login()

    def test_get_user_comments_success(self):
        result = self.tq.get_user_comments()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for comment in result:
            self.assertRegex(comment, '[0-9]+')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tq = None


if __name__ == '__main__':
    unittest.main()
