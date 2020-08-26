# -*- coding: utf-8 -*-
import requests
import ini
from api import theqoo_api, util
from api.util import MessageTypes


class Theqoo:
    # Session
    session = requests.session()
    # User
    __theqoo_id = ''
    __theqoo_pw = ''
    # Flags
    __logged_in = False
    # Etc
    __session_file_path = None

    def __init__(self, user_id, user_pw, session_file_path: str = None, no_directly_login: bool = False):
        # Set Properties
        self.__set_theqoo_id(user_id)
        self.__set_theqoo_pw(user_pw)
        # When Parameter Not Passed
        if session_file_path is None:
            self.__session_file_path = ini.SESSION_FILE_NAME
        else:
            self.__session_file_path = session_file_path
        # Get Former Session
        former_session = theqoo_api.get_former_session(self.__session_file_path)
        # Check Former Session Alive
        if former_session is not None:
            # When Can Be Used
            self.session = former_session
            self.__logged_in = True

        if no_directly_login:
            pass
        elif not self.__logged_in:
            # When Unable To Use Former Session
            try:
                self.__logged_in = theqoo_api.do_login(
                    session=self.session,
                    login_id=self.__theqoo_id,
                    login_pw=self.__theqoo_pw,
                    session_file_name=self.__session_file_path)
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

    def get_session_file_path(self):
        return self.__session_file_path


if __name__ == "__main__":
    # tq = Theqoo(ini.THEQOO_ID, ini.THEQOO_PW)
    # theqoo_api.do_login()
    # result = theqoo_api.get_user_comments()
    # for comment in result:
    #     response = theqoo_api.delete_comment(comment)
    #     print(response)
    pass
