"""
Module for enumerating tools on the PATH so that we may use
fully qualified names when spawning new shells
"""


import os
from pathlib import Path
from typing import List

from logria.logger.default_logger import setup_default_logger

# Setup default logger
LOGGER = setup_default_logger(__name__)


class Resolver():
    """
    Resolves a tool to its fully qualified name if it exists on the user's PATH
    """

    def __init__(self):
        self._paths = {}
        self.user_home = str(Path.home())
        self.resolve_paths()

    def resolve_paths(self) -> None:
        """
        Fill the paths dictionary with data
        """
        paths = os.environ.get('PATH', None)
        if paths is None:
            LOGGER.info('PATH environment variable does not exist!')
        else:
            # Iterate in reverse so we resolve tools in local paths after system paths
            for path in paths.split(':')[::-1]:
                # Try and remove the file from the path to include the parent dir
                if os.path.isfile(path):
                    path = '/'.join(path.split('/')[:-1])
                    if os.path.isfile(path):
                        print(
                            f'{path} listed in PATH environment variable, refers to file!')
                        continue
                try:
                    programs = os.listdir(self.resolve_home_dir(path))
                except FileNotFoundError:
                    print(
                        f'{path} listed in PATH environment variable, but does not exist!')
                    continue
                self._paths.update(
                    {programs: f'{path}/{programs}' for programs in programs}
                )

    def get(self, program: str) -> str:
        """
        Get a program's fully qualified path if it exists
        """
        return self._paths.get(program, program)

    def resolve_home_dir(self, part: str) -> str:
        """
        Resolves the user's home directory
        """
        if '~' in part:
            return part.replace('~', self.user_home)
        elif '$HOME' in part:
            return part.replace('$HOME', self.user_home)
        return part

    def resolve_command_as_string(self, command: str) -> str:
        """
        Replace all programs on the path with their fully qualified counterparts as a string
        """
        return ' '.join(self.resolve_command_as_list(command))

    def resolve_command_as_list(self, command: str) -> List[str]:
        """
        Replace all programs on the path with their fully qualified counterparts as a list
        """
        command_parts = command.split(' ')
        new_command = []
        for part in command_parts:
            resolved_part = self.get(part)
            resolved_part = self.resolve_home_dir(resolved_part)
            new_command.append(resolved_part)
        return new_command

    def resolve_file_as_list(self, filepath: str) -> List[str]:
        """
        Resolve a file path as a list of folders
        """
        path_parts = filepath.split('/')
        new_path = []
        for part in path_parts:
            new_path.append(self.resolve_home_dir(part))
        return new_path

    def resolve_file_as_str(self, filepath: str) -> str:
        """
        Resolve a file path as a slash-separated string
        """
        return '/'.join(self.resolve_file_as_list(filepath))
