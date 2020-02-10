"""
Classes to handle saving sessions
"""


import json
import os
from pathlib import Path

from logria.utilities.constants import SAVED_SESSIONS_PATH


class SessionHandler():
    """
    Class that manages sessions for the user
    """

    def __init__(self):
        self._commands: dict = {}
        self._type = ''

    def load_session(self, item: int) -> dict:
        """
        Load data for a session
        """
        out_d = {}
        if item in SessionHandler().sessions():
            name = SessionHandler().sessions()[item]
            with open(Path(SAVED_SESSIONS_PATH, name), 'r') as f:
                out_d = json.loads(f.read())
        return out_d

    def save_session(self, name: str, commands: list, type_: str) -> None:
        """
        Save a session to the sessions directory
        """
        out_json = {'commands': commands, 'type': type_}
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
    s = SessionHandler()
    print(s.sessions())
    print(s.show_sessions())
    print(s.load_session(0).get('commands')[0])
    # from logria.utilities.command_parser import Resolver
    # r = Resolver()
    # command = 'python sample_streams/generate_test_logs.py'
    # cmd = r.resolve_command_as_list(command)
    # s.save_session('Generate Test Logs', [cmd])
