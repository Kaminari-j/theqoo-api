# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
from multiprocessing import Process, Queue
import requests
from eraser import ini

INIT_URL = 'https://theqoo.net/index.php'


class Theqoo:
    # Session
    session = None
    # User
    __theqoo_id = ''
    __theqoo_pw = ''
    # Flags
    __logged_in = False
    # Etc
    __index_page_id = 'cate_index'

    def __init__(self, user_id, user_pw):
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Host': 'theqoo.net'
        }

        self.__set_theqoo_id(user_id)
        self.__set_theqoo_pw(user_pw)

    def __set_theqoo_id(self, theqoo_id):
        if theqoo_id is None or theqoo_id.strip() == '' or theqoo_id == 'YOUR THEQOO ID':
            raise ValueError('THEQOO_ID 가 설정되지 않았습니다')
        else:
            self.__theqoo_id = theqoo_id

    def __set_theqoo_pw(self, theqoo_pw):
        if theqoo_pw is None or theqoo_pw.strip() == '' or theqoo_pw == 'YOUR THEQOO ID':
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

    def login(self):
        url = f'{INIT_URL}?mid=cate_index&act=dispMemberLoginForm'
        data = {
            'error_return_url': '/index.php?mid=cate_index&act=dispMemberLoginForm',
            'mid': 'cate_index',
            'act': 'procMemberLogin',
            'xe_validator_id': 'modules/member/skins/sketchbook5_member_skin/1',
            'user_id': self.__theqoo_id,
            'password': self.__theqoo_pw,
            'keep_signed': 'N'
        }

        login_res = self.session.post(url, data=data)
        response_bs = bs(login_res.text, features="html.parser")
        login_error = response_bs.find('div', {'class', 'message error'})

        # Check StatusCode
        if login_res.status_code != 200:
            raise ConnectionError(f'Failed To Login (Status Code: {login_res.status_code})')
        # Check Login Error
        elif login_error is not None:
            raise ConnectionError(f'Failed To Login: {login_error.text}')
        else:
            self.__logged_in = True

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
        response = self.session.post(url, data=xml_payload.encode('utf-8'))
        response_bs = bs(response.text, features="html.parser")
        result_code = int(response_bs.find('error').text)
        result_msg = response_bs.find('message').text

        # Check StatusCode
        if response.status_code != 200:
            raise ConnectionError(f'Failed To Delete Comment (Status Code: {response.status_code})')
        # Check ResultCode
        elif result_code != 0:
            raise RuntimeError(f'Failed To Delete Comment (Result Message: {result_msg})')
        else:
            return f'Comment: {comment_srl} Result: {result_msg}'

    def get_user_comments(self):
        # Todo: Save Cache Function
        # Todo: DTO?

        result = []

        # Get Comment Pages
        page_num = 1
        while True:
            # Make Url
            url = f'{INIT_URL}?act=dispSejin7940_commentOwnComment&mid=cate_index&page={page_num}'

            # Make Request
            response = self.session.get(url)

            # Check StatusCode
            if response.status_code != 200:
                raise ConnectionError(f'Failed To Get Comments (Status Code: {response.status_code})')

            # Convert Response To BeautifulSoup
            response_bs = bs(response.text, features="html.parser")

            # Get Comments From Page
            comments = response_bs.findAll('td', {'class', 'title'})

            # When There's No Comments
            if len(comments) < 1:
                break

            # Get Comment Srl From Each Comment And Add To List
            for comment in comments:
                result.append(comment.findAll('a')[-1]['href'].split('_')[-1])

            # Increase page_num
            page_num += 1

        # Return Comment List
        return result


if __name__ == "__main__":
    tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
    tq.login()
    response = tq.delete_comment(1581141940)
    print(response)
    pass
