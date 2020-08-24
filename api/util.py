import requests
import pickle


def save_session(session_file_path: str, session: requests.session):
    try:
        with open(session_file_path, 'wb') as f:
            pickle.dump(session, f)
            return True
    except IOError:
        return False


def load_session(session_file_path: str):
    try:
        with open(session_file_path, 'rb') as f:
            session = pickle.load(f)
        return session
    except IOError:
        return None
