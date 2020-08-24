# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import ini
from api import util
from api.util import MessageTypes

INIT_URL = 'https://theqoo.net/index.php'


class Theqoo:
    # Session
    session = requests.session()
    # User
    __theqoo_id = ''
    __theqoo_pw = ''
    # Flags
    __logged_in = False
    # Etc
    __index_page_id = 'cate_index'

    def __init__(self, user_id, user_pw, session_file_path: str = None, no_directly_login: bool = None):
        # Set Properties
        self.__set_theqoo_id(user_id)
        self.__set_theqoo_pw(user_pw)
        # When Parameter Not Passed
        if session_file_path is None:
            session_file_path = ini.SESSION_FILE_NAME

        if no_directly_login:
            pass
        else:
            # Get Former Session
            former_session = self.get_former_session(session_file_path)
            # Check Former Session Alive
            if former_session is not None:
                # When Can Be Used
                self.session = former_session
                self.__logged_in = True
            else:
                # When Unable To Use Former Session
                try:
                    self.do_login(session_file_name=session_file_path)
                except ConnectionError as e:
                    util.print_message(message_type=MessageTypes.ERROR,
                                       message=f'다음과 같은 이유로 로그인에 실패하였습니다. {e.strerror}')
        # Set Headers To Session
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Host': 'theqoo.net'
        }

    def __set_theqoo_id(self, theqoo_id):
        if theqoo_id is None or theqoo_id.strip() == '' or theqoo_id == 'THEQOO ID':
            raise ValueError('THEQOO_ID 가 설정되지 않았습니다')
        else:
            self.__theqoo_id = theqoo_id

    def __set_theqoo_pw(self, theqoo_pw):
        if theqoo_pw is None or theqoo_pw.strip() == '' or theqoo_pw == 'THEQOO ID':
            raise ValueError('THEQOO_PW 가 설정되지 않았습니다')
        else:
            self.__theqoo_pw = theqoo_pw

    def has_session(self):
        return self.session is not None

    def is_logged_in(self):
        return self.__logged_in

    def get_theqoo_id(self):
        return self.__theqoo_id

    def get_theqoo_pw(self):
        return self.__theqoo_pw

    @staticmethod
    def get_former_session(session_file_name: str):
        # Get Session From File
        s = util.load_session(session_file_name)
        # When Got No Session
        if s is None:
            return None
        # Check Session With Make A Test Request To Open My Page
        url = f'{INIT_URL}?act=dispMemberInfo'
        # Make Request
        res = s.get(url)
        find_result = len(bs(res.text, features="html.parser").findAll('div', {'class', 'login-header'}))
        # When Logged On Successfully, Length Of find_result Should Be 0
        if find_result != 0:
            return None
        else:
            return s

    def do_login(self, session_file_name: str):
        if self.is_logged_in():
            return

        url = f'{INIT_URL}?mid=cate_index&act=dispMemberLoginForm'
        data = {
            'error_return_url': '/index.php?mid=cate_index&act=dispMemberLoginForm',
            'mid': 'cate_index',
            'act': 'procMemberLogin',
            'xe_validator_id': 'modules/member/skins/sketchbook5_member_skin/1',
            'user_id': self.__theqoo_id,
            'password': self.__theqoo_pw,
            'keep_signed': 'Y'
        }

        login_res = self.session.post(url, data=data)
        response_bs = bs(login_res.text, features="html.parser")
        login_error = response_bs.find('div', {'class', 'message error'})

        # Store Session To File
        util.save_session(session_file_name, self.session)

        # Check StatusCode
        if login_res.status_code != 200:
            raise ConnectionError(f'Failed To Login (Status Code: {login_res.status_code})')
        # Check Login Error
        elif login_error is not None:
            raise ConnectionError(login_error.text)
        # Login Success
        else:
            self.__logged_in = True
            util.print_message(message_type=MessageTypes.SYSTEM,
                               message='정상적으로 로그인 되었습니다.')

    def delete_comment(self, comment_srl):
        xml_payload = f'<?xml version="1.0" encoding="utf-8" ?>' \
                      f'<methodCall>' \
                      f'<params>' \
                      f'<target_srl><![CDATA[{comment_srl}]]></target_srl>' \
                      f'<cur_mid><![CDATA[cate_index]]></cur_mid>' \
                      f'<mid><![CDATA[cate_index]]></mid>' \
                      f'<module><![CDATA[sejin7940_comment]]></module>' \
                      f'<act><![CDATA[procSejin7940_commentDeleteComment]]></act>' \
                      f'</params>' \
                      f'</methodCall>'
        url = f'{INIT_URL}'
        res = self.session.post(url, data=xml_payload.encode('utf-8'))
        bsobj = bs(res.text, features="html.parser")
        result_code = int(bsobj.find('error').text)
        result_msg = bsobj.find('message').text

        # Check StatusCode
        if res.status_code != 200:
            raise ConnectionError(f'Failed To Delete Comment (Status Code: {res.status_code})')
        # Check ResultCode
        elif result_code != 0:
            raise RuntimeError(f'Failed To Delete Comment (Result Message: {result_msg})')
        else:
            return f'Comment: {comment_srl} Result: {result_msg}'

    def get_user_comments(self):
        # Todo: Save Cache Function
        # Todo: DTO?

        comments = []

        # Get Comment Pages
        page_num = 1
        while True:
            # Make Url
            url = f'{INIT_URL}?act=dispSejin7940_commentOwnComment&mid=cate_index&page={page_num}'

            # Make Request
            res = self.session.get(url)

            # Check StatusCode
            if res.status_code != 200:
                raise ConnectionError(f'Failed To Get Comments (Status Code: {res.status_code})')

            # Convert Response To BeautifulSoup
            response_bs = bs(res.text, features="html.parser")

            # Get Comments From Page
            bs_comments = response_bs.findAll('td', {'class', 'title'})

            # When There's No Comments
            if len(bs_comments) < 1:
                break

            # Get Comment Srl From Each Comment And Add To List
            for c in bs_comments:
                comments.append(c.findAll('a')[-1]['href'].split('_')[-1])

            # Increase page_num
            page_num += 1

        # Return Comment List
        return comments


if __name__ == "__main__":
    tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
    tq.__do_login()
    result = tq.get_user_comments()
    for comment in result:
        response = tq.delete_comment(comment)
        print(response)
    pass
