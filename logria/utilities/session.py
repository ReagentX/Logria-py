"""
Classes to handle saving sessions
"""


import os
import json
from pathlib import Path


from logria.utilities.constants import SAVED_SESSIONS_PATH
from logria.communication.input_handler import CommandInputStream


class SessionHandler():
    def __init__(self):
        self._commands: dict = {}

    def load_session(self, item: int) -> dict:
        """
        Load data for a session
        """
        out_d = {}
        if item in SessionHandler().sessions():
            name = SessionHandler().sessions()[item]
            with open(Path(SAVED_SESSIONS_PATH, name), 'w') as f:
                out_d = json.loads(f.read())
        return out_d

    def save_session(self, name: str, commands: list) -> None:
        """
        Save a session to the sessions directory
        """
        out_json = {'commands': commands}
        with open(Path(SAVED_SESSIONS_PATH, name), 'w') as f:
            f.write(json.dumps(out_json, indent=4))

    @classmethod
    def sessions(cls) -> dict:
        """
        Get the existing sessions as a dict
        """
        sessions = os.listdir(SAVED_SESSIONS_PATH)
        return dict(zip(range(0, len(sessions)), sessions))

    @classmethod
    def show_sessions(cls) -> dict:
        """
        Get the existing sessions as a list for output
        """
        sessions = os.listdir(SAVED_SESSIONS_PATH)
        return [f'{i}: {v}' for i, v in enumerate(sessions)]


if __name__ == '__main__':
    from logria.utilities.command_parser import Resolver
    s = SessionHandler()
    print(s.sessions())
    print(s.show_sessions())
    # r = Resolver()
    # command = 'python logria/communication/generate_test_logs.py'
    # cmd = r.resolve_command_as_list(command)
    # s.save_session('Generate Test Logs', [cmd])
