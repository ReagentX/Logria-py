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
        return self._paths.get(program, program)


if __name__ == '__main__':
    r = Resolver()
    print(r.get('tail'))
    print(r.get('tail23'))
