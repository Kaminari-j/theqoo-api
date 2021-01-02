from api import theqoo_api
from api.theqoo import Theqoo
import ini


def delete_document_with_id(document_id: str):
    tq = Theqoo(
        user_id=ini.THEQOO_ID,
        user_pw=ini.THEQOO_PW,
        session_file_name=f'./files/{ini.SESSION_FILE_NAME}')
    tq.do_delete_document(document_id)


if __name__ == '__main__':
    delete_document_with_id('document_srl')
