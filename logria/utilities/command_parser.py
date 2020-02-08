"""
Module for enumerating tools on the PATH so that we may use
fully qualified names when spawning new shells
"""


import os


from logria.logger.default_logger import setup_default_logger

# Setup default logger
LOGGER = setup_default_logger(__name__)


class Resolver():
    """
    Resolves a tool to its fully qualified name if it exists on the user's PATH
    """
    def __init__(self):
        self._paths = {}
        self.resolve_paths()

    def resolve_paths(self) -> None:
        """
        Fill the paths dictionary with data
        """
        paths = os.environ.get('PATH', None)
        if paths is None:
            LOGGER.info('PATH environment variable does not exist!')
            return None
        for path in paths.split(':'):
            programs = os.listdir(path)
            self._paths.update(dict([(programs, f'{path}/{programs}') for programs in programs]))

    def get(self, program: str) -> str:
        """
        Get a program's fully qualified path if it exists
        """
        return self._paths.get(program, program)

    def resolve_command_as_string(self, command: str) -> str:
        """
        Replace all programs on the path with their fully qualified counterparts as a string
        """
        command_parts = command.split(' ')
        new_command = ''
        for part in command_parts:
            resolved_part = self.get(part)
            new_command += ' ' + resolved_part
        return new_command

    def resolve_command_as_list(self, command: str) -> list:
        """
        Replace all programs on the path with their fully qualified counterparts as a list
        """
        command_parts = command.split(' ')
        new_command = []
        for part in command_parts:
            resolved_part = self.get(part)
            new_command.append(resolved_part)
        return new_command

if __name__ == '__main__':
    r = Resolver()
    print('  path\t', r.get('tail'))
    print('nopath\t', r.get('tail23'))
    print(r.resolve_command_as_string('tail -f file.txt | grep [^a-z](.*?)<'))
    print(r.resolve_command_as_list('tail -f file.txt | grep [^a-z](.*?)<'))