import os

import requests
from bs4 import BeautifulSoup as bs
from api import util
from api.util import MessageTypes

INIT_URL = 'https://theqoo.net/index.php'
INDEX_PAGE_ID = 'cate_index'


class Actions:
    MY_PAGE = 'dispMemberInfo'
    LOGIN_FORM = 'dispMemberLoginForm'
    OWN_COMMENTS = 'dispSejin7940_commentOwnComment'
    MOD_COMMENT = 'sejin7940_comment'
    PROC_DELETE_COMMENT = 'procSejin7940_commentDeleteComment'
    PROC_LOGIN = 'procMemberLogin'
    OWN_DOCUMENTS = 'dispMemberOwnDocument'
    PROC_DELETE_DOCUMENT = 'procMemberDeleteMyDocuments'
    MOD_MEMBER = 'member'


class Document:
    category_nm = None
    title = None
    srl = None

    def __init__(self, category_nm: str, title: str, srl: str):
        self.category_nm = category_nm
        self.title = title
        self.srl = srl


def get_former_session(session_file_name: str):
    # Check If File Exists
    if not os.path.exists(session_file_name):
        return None
    # Get Session From File
    with util.load_session(session_file_name) as s:
        # When Got No Session
        if s is None:
            return None
        # Check Session With Make A Test Request To Open 'My Page'
        res = s.get(f'{INIT_URL}?act={Actions.MY_PAGE}')
        find_result = len(bs(res.text, features="html.parser").findAll('div', {'class', 'login-header'}))
        # When Logged On Successfully, Length Of find_result Should Be 0
        if find_result != 0:
            return None
        # Return Session Object
        return s


def do_login(session: requests.Session, login_id: str, login_pw: str, session_file_name: str):
    url = f'{INIT_URL}?mid={INDEX_PAGE_ID}&act={Actions.LOGIN_FORM}'
    data = {
        'error_return_url': f'/index.php?mid={INDEX_PAGE_ID}&act={Actions.LOGIN_FORM}',
        'mid': INDEX_PAGE_ID,
        'act': Actions.PROC_LOGIN,
        'xe_validator_id': 'modules/member/skins/sketchbook5_member_skin/1',
        'user_id': login_id,
        'password': login_pw,
        'keep_signed': 'N'
    }
    # Todo: Encrypt

    login_res = session.post(url, data=data)
    response_bs = bs(login_res.text, features="html.parser")
    login_error = response_bs.find('div', {'class', 'message error'})

    # Store Session To File
    util.save_session(session_file_name, session)

    # Check StatusCode
    if login_res.status_code != 200:
        raise ConnectionError(f'Failed To Login (Status Code: {login_res.status_code})')
    # Check Login Error
    elif login_error is not None:
        raise AttributeError(login_error.text)
    # Login Success
    else:
        util.print_message(message_type=MessageTypes.SYSTEM,
                           message='정상적으로 로그인 되었습니다.')
        return True


def delete_comment(session: requests.Session, comment_srl):
    xml_payload = f'<?xml version="1.0" encoding="utf-8" ?>' \
                  f'<methodCall>' \
                  f'<params>' \
                  f'<target_srl><![CDATA[{comment_srl}]]></target_srl>' \
                  f'<cur_mid><![CDATA[{INDEX_PAGE_ID}]]></cur_mid>' \
                  f'<mid><![CDATA[{INDEX_PAGE_ID}]]></mid>' \
                  f'<module><![CDATA[{Actions.MOD_COMMENT}]]></module>' \
                  f'<act><![CDATA[{Actions.PROC_DELETE_COMMENT}]]></act>' \
                  f'</params>' \
                  f'</methodCall>'
    url = f'{INIT_URL}'
    res = session.post(url, data=xml_payload.encode('utf-8'))
    # Check StatusCode
    if res.status_code != 200:
        raise ConnectionError(f'Failed To Delete Comment (Status Code: {res.status_code})')
    bsobj = bs(res.text, features="html.parser")
    result_code = int(bsobj.find('error').text)
    result_msg = bsobj.find('message').text

    # Check ResultCode
    if result_code != 0:
        raise RuntimeError(f'Failed To Delete Comment (Result Message: {result_msg})')
    else:
        return f'Comment: {comment_srl} Result: {result_msg}'


def get_user_comments(session: requests.Session):
    # Todo: Save Cache Function
    # Todo: DTO?

    comments = []

    # Get Comment Pages
    page_num = 1
    while True:
        # Make Url
        url = f'{INIT_URL}?act={Actions.OWN_COMMENTS}&mid={INDEX_PAGE_ID}&page={page_num}'

        # Make Request
        res = session.get(url)

        # Check Login Status
        if is_logged_in(res) is not True:
            raise AttributeError(f'Failed To Get Documents: Not Logged In')

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


def get_user_documents(session: requests.Session):
    documents = []
    # Get Comment Pages
    page_num = 1
    while True:
        # Make Url
        url = f'{INIT_URL}?act={Actions.OWN_DOCUMENTS}&mid={INDEX_PAGE_ID}&page={page_num}'

        # Make Request
        res = session.get(url)

        # Check Login Status
        if is_logged_in(res) is not True:
            raise AttributeError(f'Failed To Get Documents: Not Logged In')

        # Check StatusCode
        if res.status_code != 200:
            raise ConnectionError(f'Failed To Get Documents (Status Code: {res.status_code})')

        # Convert Response To BeautifulSoup
        bsobj = bs(res.text, features="html.parser")

        # Get Documents From Page
        bs_documents = bsobj.findAll(
            'table', {'class', 'table table-striped table-hover member_info_table'}
        )

        # Get Table Rows
        doc_rows = bs_documents[-1]('tr')

        # Break Loop When There's No Documents
        if len(doc_rows) < 1:
            break

        # Get Comment Srl From Each Comment And Add To List
        for doc in doc_rows:
            documents.append(Document(category_nm=doc('a')[0].text,
                                      title=doc('a')[1].text,
                                      srl=doc('a')[1]['href'].split('/')[-1]))
        # Increase page_num
        page_num += 1
    # return list
    return documents


def is_logged_in(response: requests.Response) -> bool:
    login_error = bs(response.text, features="html.parser").find('div', {'class', 'login-header'})
    if login_error is None:
        return True
    else:
        return False


def delete_document(session: requests.Session, document_srl):
    xml_payload = f'<?xml version="1.0" encoding="utf-8" ?>' \
                  f'<methodCall>' \
                  f'<params>' \
                  f'<document_srls><![CDATA[{document_srl}]]></document_srls>' \
                  f'<module><![CDATA[{Actions.MOD_MEMBER}]]></module>' \
                  f'<act><![CDATA[{Actions.PROC_DELETE_DOCUMENT}]]></act>' \
                  f'</params>' \
                  f'</methodCall>'
    url = f'{INIT_URL}'
    res = session.post(url, data=xml_payload.encode('utf-8'))
    # Check StatusCode
    if res.status_code != 200:
        raise ConnectionError(f'Failed To Delete Document (Status Code: {res.status_code})')
    bsobj = bs(res.text, features="html.parser")
    result_code = int(bsobj.find('error').text)
    result_msg = bsobj.find('message').text

    # Check ResultCode
    if result_code != 0:
        raise RuntimeError(f'Failed To Delete Document (Result Message: {result_msg})')
    else:
        return f'Comment: {document_srl} Result: {result_msg}'


