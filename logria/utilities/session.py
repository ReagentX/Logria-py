"""
Classes to handle saving sessions
"""


import json
import os
from pathlib import Path
from typing import List, Union

from logria.utilities.constants import LOGRIA_ROOT, SAVED_SESSIONS_PATH


class SessionHandler():
    """
    Class that manages sessions for the user
    """

    def __init__(self):
        self._commands: List[List[str]] = []
        self._type: str = ''  # One of {'command', 'file'}
        self.folder: Path = None
        self.setup_folder()

    def set_params(self, command: List[str], type_: str) -> None:
        """
        Update the commands and parameters
        """
        self.add_command(command)
        self.set_type(type_)

    def set_type(self, type_str):
        """
        Sets the type of command
        """
        self._type = type_str

    def add_command(self, command: List[str]):
        """
        Adds the command to the list of commands
        """
        self._commands.append(command)

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

    def save_current_session(self, name: str) -> None:
        """
        Saves the current session
        """
        self.save_session(name, self._commands, self._type)

    def save_session(self, name: str, commands: Union[List[List[str]], List[str]], type_: str) -> None:
        """
        Save a session to the sessions directory
        """
        out_json = {'commands': commands, 'type': type_}
        with open(self.folder / name, 'w') as f:
            f.write(json.dumps(out_json, indent=4))

    def as_list(self) -> List[str]:
        """
        Returns a list representation of the current session
        """
        out_l = []
        out_l.append('Type:')
        out_l.append(f'  {self._type}')
        if self._type == 'command':
            out_l.append('Commands:')
            for command in self._commands:
                out_l.append(f'  {" ".join(command)}')
        elif self._type == 'file':
            out_l.append('Files:')
            for file in self._commands:
                out_l.append(f'  {"/".join(file)}')
        return out_l

    def sessions(self) -> dict:
        """
        Get the existing sessions as a dict
        """
        sessions = sorted(os.listdir(self.folder))
        return dict(zip(range(0, len(sessions)), sessions))

    def show_sessions(self) -> List[str]:
        """
        Get the existing sessions as a list for output
        """
        sessions = sorted(os.listdir(self.folder))
        return [f'{i}: {v}' for i, v in enumerate(sessions)]
