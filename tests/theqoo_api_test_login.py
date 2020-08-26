import unittest
import os
from pathlib import Path
import requests
import ini
from api import theqoo_api as api
from tests import test_setting
import responses
from varname import nameof

path = Path(test_setting.TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)

# CAUTION !!
# Don't Execute instrumented LoginTestCase Too Often In A Short Time (About 2~3 Times),
# It May Causes Blocking Your IP From Theqoo About 5 Minutes
TEST_INSTRUMENTED = False


class TestBody:
    @staticmethod
    def do_login_test(cls: unittest.TestCase, login_id: str, login_pw: str, session: requests.Session):
        res = api.do_login(session=session,
                           login_id=login_id, login_pw=login_pw,
                           session_file_name=test_setting.FILE_GARBAGE)
        cls.assertTrue(res, 'Return value should be True when login success')

    @staticmethod
    def do_login_test_attribute_error(cls: unittest.TestCase, login_id: str, login_pw: str, session: requests.Session):
        with cls.assertRaises(AttributeError):
            api.do_login(session=session,
                         login_id=login_id, login_pw=login_pw,
                         session_file_name=test_setting.FILE_GARBAGE)

    @staticmethod
    def do_login_test_connection_error(cls: unittest.TestCase, login_id: str, login_pw: str, session: requests.Session):
        with cls.assertRaises(ConnectionError):
            api.do_login(session=session,
                         login_id=login_id, login_pw=login_pw,
                         session_file_name=test_setting.FILE_GARBAGE)


@unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
class LoginTestCase_Instrumented(unittest.TestCase):
    testId = 'id'
    testPw = 'pw'

    def tearDown(self) -> None:
        if os.path.exists(test_setting.FILE_GARBAGE):
            os.remove(test_setting.FILE_GARBAGE)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_ok(self):
        with requests.session() as s:
            TestBody.do_login_test(self, session=s, login_id=ini.THEQOO_ID, login_pw=ini.THEQOO_PW)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_failed_with_id(self):
        with requests.session() as s:
            TestBody.do_login_test_attribute_error(self, session=s, login_id=self.testId, login_pw=ini.THEQOO_PW)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_failed_with_pw(self):
        with requests.session() as s:
            TestBody.do_login_test_attribute_error(self, session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)


class LoginTestCase(unittest.TestCase):
    url = f'{api.INIT_URL}?mid={api.INDEX_PAGE_ID}&act={api.Actions.LOGIN_FORM}'
    testId = 'id'
    testPw = 'pw'

    def tearDown(self) -> None:
        if os.path.exists(test_setting.FILE_GARBAGE):
            os.remove(test_setting.FILE_GARBAGE)

    @responses.activate
    def test_login_ok(self):
        responses.add(responses.POST, url=self.url, status=200)
        with requests.session() as s:
            TestBody.do_login_test(self, session=s, login_id=ini.THEQOO_ID, login_pw=ini.THEQOO_PW)

    @responses.activate
    def test_login_failed_with_connection_error(self):
        responses.add(responses.POST, url=self.url, status=404)
        with requests.session() as s:
            TestBody.do_login_test_connection_error(self, session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)

    @responses.activate
    def test_login_failed_with_id(self):
        res = r'<div class="message error"><p>존재하지 않는 회원 아이디입니다.</p></div>'
        responses.add(responses.POST, url=self.url, body=res, status=200)
        with requests.session() as s:
            TestBody.do_login_test_attribute_error(self, session=s, login_id=self.testId, login_pw=ini.THEQOO_PW)

    @responses.activate
    def test_login_failed_with_pw(self):
        res = r'<div class="message error"><p>잘못된 비밀번호입니다.</p></div>'
        responses.add(responses.POST, url=self.url, body=res, status=200)
        with requests.session() as s:
            TestBody.do_login_test_attribute_error(self, session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)


if __name__ == '__main__':
    unittest.main()
