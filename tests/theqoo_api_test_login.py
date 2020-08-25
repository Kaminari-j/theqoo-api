import unittest
import os
from pathlib import Path
import requests
import ini
from api import theqoo_api as api
from tests import test_setting

path = Path(test_setting.TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)


# CAUTION !!
# Don't Execute LoginTestCase Too Often In A Short Time (About 2~3 Times),
# It May Causes Blocking Your IP From Theqoo About 5 Minutes
class LoginTestCase(unittest.TestCase):
    testId = 'id'
    testPw = 'pw'

    def tearDown(self) -> None:
        if os.path.exists(test_setting.FILE_GARBAGE):
            os.remove(test_setting.FILE_GARBAGE)

    def test_login_ok(self):
        with requests.session() as s:
            res = api.do_login(session=s,
                               login_id=ini.THEQOO_ID, login_pw=ini.THEQOO_PW,
                               session_file_name=test_setting.FILE_GARBAGE)
            self.assertTrue(res, 'Return value should be True when login success')

    def test_login_failed_with_id(self):
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.do_login(session=s,
                             login_id=self.testId, login_pw=ini.THEQOO_PW,
                             session_file_name=test_setting.FILE_GARBAGE)

    def test_login_failed_with_pw(self):
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.do_login(session=s,
                             login_id=ini.THEQOO_ID, login_pw=self.testPw,
                             session_file_name=test_setting.FILE_GARBAGE)


if __name__ == '__main__':
    unittest.main()
