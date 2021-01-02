import requests
import pickle


class MessageTypes:
    SYSTEM = 'SYSTEM'
    ERROR = 'ERROR'


def save_session(session_file_path: str, session: requests.session) -> bool:
    try:
        with open(session_file_path, 'wb') as f:
            pickle.dump(session, f)
            return True
    except IOError:
        return False


def load_session(session_file_path: str) -> requests.Session:
    session = None
    try:
        with open(session_file_path, 'rb') as f:
            session = pickle.load(f)
        return session
    except IOError:
        return session


def print_message(message_type: MessageTypes, message: str):
    print(f'{message_type}: {message}')
