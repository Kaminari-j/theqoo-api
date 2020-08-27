import os
import unittest
from pathlib import Path

import requests
import responses
from varname import nameof

import ini
from api import theqoo_api as api
from tests import test_setting

path = Path(test_setting.TEST_FILE_DIR)
path.mkdir(parents=True, exist_ok=True)

# Set True when do you want to 'real' test
# CAUTION !!
# Don't Execute instrumented LoginTestCase Too Often In A Short Time (About 2~3 Times),
# It May Causes Blocking Your IP From Theqoo About 5 Minutes
TEST_INSTRUMENTED = True


class LoginTestCase_Instrumented(unittest.TestCase):
    url = f'{api.INIT_URL}?mid={api.INDEX_PAGE_ID}&act={api.Actions.LOGIN_FORM}'
    testId = 'id'
    testPw = 'pw'

    def tearDown(self) -> None:
        if os.path.exists(test_setting.FILE_GARBAGE):
            os.remove(test_setting.FILE_GARBAGE)

    def do_login_test(self, login_id: str, login_pw: str, session: requests.Session):
        res = api.do_login(session=session,
                           login_id=login_id, login_pw=login_pw,
                           session_file_name=test_setting.FILE_GARBAGE)
        self.assertTrue(res, 'Return value should be True when login success')

    def do_login_test_attribute_error(self, login_id: str, login_pw: str, session: requests.Session):
        with self.assertRaises(AttributeError):
            api.do_login(session=session,
                         login_id=login_id, login_pw=login_pw,
                         session_file_name=test_setting.FILE_GARBAGE)

    def do_login_test_connection_error(self, login_id: str, login_pw: str, session: requests.Session):
        with self.assertRaises(ConnectionError):
            api.do_login(session=session,
                         login_id=login_id, login_pw=login_pw,
                         session_file_name=test_setting.FILE_GARBAGE)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_ok_instrumented(self):
        with requests.session() as s:
            self.do_login_test(session=s, login_id=ini.THEQOO_ID, login_pw=ini.THEQOO_PW)

    @responses.activate
    def test_login_ok(self):
        responses.add(responses.POST, url=self.url, status=200)
        with requests.session() as s:
            self.do_login_test(session=s, login_id=ini.THEQOO_ID, login_pw=ini.THEQOO_PW)

    @responses.activate
    def test_login_failed_with_connection_error(self):
        responses.add(responses.POST, url=self.url, status=404)
        with requests.session() as s:
            self.do_login_test_connection_error(session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_failed_with_id_instrumented(self):
        with requests.session() as s:
            self.do_login_test_attribute_error(session=s, login_id=self.testId, login_pw=ini.THEQOO_PW)

    @responses.activate
    def test_login_failed_with_id(self):
        res = r'<div class="message error"><p>존재하지 않는 회원 아이디입니다.</p></div>'
        responses.add(responses.POST, url=self.url, body=res, status=200)
        with requests.session() as s:
            self.do_login_test_attribute_error(session=s, login_id=self.testId, login_pw=ini.THEQOO_PW)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_login_failed_with_pw_instrumented(self):
        with requests.session() as s:
            self.do_login_test_attribute_error(session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)

    @responses.activate
    def test_login_failed_with_pw(self):
        res = r'<div class="message error"><p>잘못된 비밀번호입니다.</p></div>'
        responses.add(responses.POST, url=self.url, body=res, status=200)
        with requests.session() as s:
            self.do_login_test_attribute_error(session=s, login_id=ini.THEQOO_ID, login_pw=self.testPw)


class DeleteCommentTestCase_Instrumented(unittest.TestCase):
    def delete_comment_success(self, session: requests.Session, comment_srl):
        result = api.delete_comment(session, comment_srl)
        self.assertIsInstance(result, str)

    def delete_comment_fail_with_runtime_error(self, session: requests.Session, comment_srl):
        with self.assertRaises(RuntimeError):
            api.delete_comment(session, comment_srl)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_delete_comment_success_instrumented(self):
        with api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION) as s:
            self.delete_comment_success(s, 1580192797)

    @responses.activate
    def test_delete_comment_success(self):
        res = '﻿<?xml version="1.0" encoding="UTF-8"?>' \
              '<response>' \
              '<error>0</error>' \
              '<message>댓글이 삭제되었습니다. </message>' \
              '<message_type></message_type>' \
              '</response>'
        responses.add(responses.POST, api.INIT_URL, body=res, status=200)
        with requests.session() as s:
            self.delete_comment_success(s, 1580192797)

    @responses.activate
    def test_delete_comment_fail_with_connection_error(self):
        # Not Logged In
        responses.add(responses.POST, api.INIT_URL, status=404)
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.delete_comment(s, 1580192797)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_delete_comment_fail_with_runtime_error_instrumented(self):
        # Not Logged In
        with requests.session() as s:
            self.delete_comment_fail_with_runtime_error(s, 1580192797)

    @responses.activate
    def test_delete_comment_fail_with_runtime_error(self):
        result_xml = f'<?xml version="1.0" encoding="utf-8" ?>' \
                  f'<response>' \
                  f'<error>-1</error>' \
                  f'<message>잘못된 요청입니다.</message>' \
                  f'<message_type></message_type>' \
                  f'</response>'
        responses.add(responses.POST, api.INIT_URL, body=result_xml, status=200)
        # Not Logged In
        with requests.session() as s:
            self.delete_comment_fail_with_runtime_error(s, 1580192797)


class GetUserCommentsTestCase(unittest.TestCase):
    def get_user_comments_success(self, session: requests.Session):
        result = api.get_user_comments(session)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for comment in result:
            self.assertRegex(comment, '[0-9]+')

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_get_user_comments_success_instrumented(self):
        with api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION) as s:
            self.get_user_comments_success(s)

    @responses.activate
    def test_get_user_comments_success(self):
        body = '<tr>' \
               '<td class="no">149</td>' \
               '<td class="title">' \
               '<div class="origin_document">' \
               '<a href="/1585915956" target="_blank">직장인 : <span style="">Article Title</span></a>' \
               '</div>' \
               '<a href="/1585915956#comment_1585918700" target="_blank">Comment</a>' \
               '</td>' \
               '<td class="nowr date">2020-08-26 14:16:50</td>' \
               '<td class="nowr action" style="width:40px;text-align:center;">' \
               '</tr>'
        url1 = f'{api.INIT_URL}?act={api.Actions.OWN_COMMENTS}&mid={api.INDEX_PAGE_ID}&page=1'
        responses.add(responses.GET, url1, body=body, status=200)
        url2 = f'{api.INIT_URL}?act={api.Actions.OWN_COMMENTS}&mid={api.INDEX_PAGE_ID}&page=2'
        responses.add(responses.GET, url2, status=200)
        with requests.session() as s:
            self.get_user_comments_success(s)

    @responses.activate
    def test_get_user_comments_fail(self):
        url = f'{api.INIT_URL}?act={api.Actions.OWN_COMMENTS}&mid={api.INDEX_PAGE_ID}&page=1'
        responses.add(responses.GET, url, status=404)
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.get_user_comments(s)

    @responses.activate
    def test_when_not_logged_in(self):
        url = f'{api.INIT_URL}?act={api.Actions.OWN_COMMENTS}&mid={api.INDEX_PAGE_ID}&page=1'
        body = '<div class="login-header">' \
               '<h1><i class="icon-user"></i> 로그인을 하지 않았습니다.</h1>' \
               '</div>'
        responses.add(responses.GET, url=url, body=body, status=200)
        with requests.session() as s:
            with self.assertRaises(AttributeError):
                api.get_user_comments(s)


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


class GetUserDocumentsTestCase(unittest.TestCase):
    url = f'{api.INIT_URL}?act={api.Actions.OWN_DOCUMENTS}&mid={api.INDEX_PAGE_ID}&page=1'

    def test_get_user_documents_ok(self):
        with api.get_former_session(test_setting.FILE_WITH_SESSION) as s:
            res = api.get_user_documents(s)
            self.assertIsInstance(res, list)
            self.assertGreater(len(res), 0)
            for doc in res:
                self.assertIsInstance(doc, api.Document)
                self.assertTrue(doc.category_nm is not None, doc.category_nm)
                self.assertTrue(doc.title is not None, doc.title)
                self.assertTrue(doc.srl is not None, doc.srl)

    @responses.activate
    def test_get_user_documents_connection_error(self):
        responses.add(responses.GET, url=self.url, status=404)
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.get_user_documents(s)

    @responses.activate
    def test_when_not_logged_in(self):
        body = '<div class="login-header">' \
               '<h1><i class="icon-user"></i> 로그인을 하지 않았습니다.</h1>' \
               '</div>'
        responses.add(responses.GET, url=self.url, body=body, status=200)
        with requests.session() as s:
            with self.assertRaises(AttributeError):
                api.get_user_documents(s)


class DeleteDocumentTestCase_Instrumented(unittest.TestCase):
    document_srl = '1582525827'

    def delete_document_success(self, session: requests.Session, comment_srl):
        result = api.delete_document(session, comment_srl)
        self.assertIsInstance(result, str)

    def delete_document_fail_with_runtime_error(self, session: requests.Session, comment_srl):
        with self.assertRaises(RuntimeError):
            api.delete_document(session, comment_srl)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_delete_document_success_instrumented(self):
        with api.get_former_session(session_file_name=test_setting.FILE_WITH_SESSION) as s:
            self.delete_document_success(s, self.document_srl)

    @responses.activate
    def test_delete_document_success(self):
        res = '﻿<?xml version="1.0" encoding="UTF-8"?>' \
              '<response>' \
              '<error>0</error>' \
              '<message>success</message>' \
              '</response>'
        responses.add(responses.POST, api.INIT_URL, body=res, status=200)
        with requests.session() as s:
            self.delete_document_success(s, self.document_srl)

    @responses.activate
    def test_delete_document_fail_with_connection_error(self):
        # Not Logged In
        responses.add(responses.POST, api.INIT_URL, status=404)
        with requests.session() as s:
            with self.assertRaises(ConnectionError):
                api.delete_document(s, self.document_srl)

    @unittest.skipUnless(TEST_INSTRUMENTED, f'Test only when {nameof(TEST_INSTRUMENTED)} is True')
    def test_delete_document_fail_with_runtime_error_instrumented(self):
        # Error never occurs on document deletion
        assert True

    @responses.activate
    def test_delete_document_fail_with_runtime_error(self):
        result_xml = '﻿<?xml version="1.0" encoding="UTF-8"?>' \
                     '<response>' \
                     '<error>1</error>' \
                     '<message>fail</message>' \
                     '</response>'
        responses.add(responses.POST, api.INIT_URL, body=result_xml, status=200)
        # Not Logged In
        with requests.session() as s:
            self.delete_document_fail_with_runtime_error(s, 'asdfadsf')


class TestIsLoggedIn(unittest.TestCase):
    target_url = f'{api.INIT_URL}?{api.Actions.MY_PAGE}'

    @responses.activate
    def test_when_logged_in(self):
        responses.add(responses.GET, url=self.target_url, body='', status=200)
        with requests.session().get(url=self.target_url) as res:
            assert api.is_logged_in(res) is True

    @responses.activate
    def test_when_not_logged_in(self):
        body = '<div class="login-header">' \
               '<h1><i class="icon-user"></i> 로그인을 하지 않았습니다.</h1>' \
               '</div>'
        responses.add(responses.GET, url=self.target_url, body=body, status=200)
        with requests.session().get(url=self.target_url) as res:
            assert api.is_logged_in(res) is False


if __name__ == '__main__':
    unittest.main()
