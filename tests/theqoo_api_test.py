import unittest
import os
from pathlib import Path
import requests
import ini
from api import theqoo_api as api
from tests import test_setting

path = Path(test_setting.TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)


class DeleteCommentTestCase(unittest.TestCase):
    def test_delete_comment_success(self):
        with api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION) as s:
            result = api.delete_comment(s, 1580192797)
            self.assertIsInstance(result, str)

    def test_delete_comment_fail(self):
        # Not Logged In
        with requests.session() as s:
            with self.assertRaises(RuntimeError):
                api.delete_comment(s, 1580192797)


class GetUserCommentsTestCase(unittest.TestCase):
    def test_get_user_comments_success(self):
        with api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION) as s:
            result = api.get_user_comments(s)
            self.assertIsInstance(result, list)
            self.assertGreater(len(result), 0)
            for comment in result:
                self.assertRegex(comment, '[0-9]+')


class GetFormerSessionTestCase_With_Session(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(test_setting.FILE_WITH_SESSION):
            with requests.session() as s:
                api.do_login(s, ini.THEQOO_ID, ini.THEQOO_PW, test_setting.FILE_WITH_SESSION)

    def test_get_former_session_got_session(self):
        res = api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION)
        self.assertIsNotNone(res)
        self.assertIsInstance(res, requests.Session)


class GetFormerSessionTestCase_With_No_Session(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not os.path.exists(test_setting.FILE_NO_SESSION):
            try:
                with requests.session() as s:
                    api.do_login(session=s,
                                 login_id='fakeId', login_pw='fakePw',
                                 session_file_name=test_setting.FILE_NO_SESSION)
            except ConnectionError:
                pass

    def test_get_former_session_no_session_file(self):
        # When There's No File
        res = api.get_former_session('File Nothing')
        self.assertIsNone(res, "None should be returned when there's no file")

    def test_get_former_session_no_session(self):
        res = api.get_former_session(session_file_name=test_setting.FILE_NO_SESSION)
        self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main()
