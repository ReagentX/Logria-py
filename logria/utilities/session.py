"""
Classes to handle saving sessions
"""


import json
import os
from pathlib import Path
from typing import List

from logria.utilities.constants import LOGRIA_ROOT, SAVED_SESSIONS_PATH


class SessionHandler():
    """
    Class that manages sessions for the user
    """

    def __init__(self):
        self._commands: dict = {}
        self._type: str = ''
        self.folder: Path = None
        self.setup_folder()

    def setup_folder(self):
        """
        Set workspace folder, create if nonexistent
        """
        home = str(Path.home())
        if Path(home, LOGRIA_ROOT).exists():
            pass
        else:
            os.mkdir(Path(home, LOGRIA_ROOT))
        if Path(home, SAVED_SESSIONS_PATH).exists():
            pass
        else:
            os.mkdir(Path(home, SAVED_SESSIONS_PATH))
        self.folder = Path(home, SAVED_SESSIONS_PATH)

    def load_session(self, item: int) -> dict:
        """
        Load data for a session
        """
        out_d = {}
        if item in SessionHandler().sessions():
            name = SessionHandler().sessions()[item]
            with open(self.folder / name, 'r') as f:
                out_d = json.loads(f.read())
        return out_d

    def save_session(self, name: str, commands: List[str], type_: str) -> None:
        """
        Save a session to the sessions directory
        """
        out_json = {'commands': commands, 'type': type_}
        with open(self.folder / name, 'w') as f:
            f.write(json.dumps(out_json, indent=4))

    def sessions(self) -> dict:
        """
        Get the existing sessions as a dict
        """
        sessions = os.listdir(self.folder)
        return dict(zip(range(0, len(sessions)), sessions))

    def show_sessions(self) -> dict:
        """
        Get the existing sessions as a list for output
        """
        sessions = os.listdir(self.folder)
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
