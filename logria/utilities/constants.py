"""
Constants used throughout the application
"""

from pathlib import Path

# Patterns
ANSI_COLOR_PATTERN = r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]'

# Paths
USER_HOME = str(Path.home())
LOGRIA_ROOT = 'logria'
SAVED_PATTERNS_PATH = f'{LOGRIA_ROOT}/patterns'
SAVED_SESSIONS_PATH = f'{LOGRIA_ROOT}/sessions'

# Messages
START_MESSAGE = 'Enter a new command to open a stream, choose a saved one from the list, or enter `:config` to configure. Enter `:q` to quit.'

# Config messages
CONFIG_START_MESSAGES = [
    'Saved data paths:',
    f'Parsers:  {USER_HOME}/{SAVED_PATTERNS_PATH}',
    f'Sessions: {USER_HOME}/{SAVED_SESSIONS_PATH}',
    'To configure new parameters, enter `session` or `parser`'
]
CREATE_SESSION_START_MESSAGES = [
    'To create a session, enter a type, either `command` or `file`.'
]

# Session Strings
SESSION_ADD_COMMAND = 'Enter a command to open pipes to:'
SESSION_SHOULD_CONTINUE_COMMAND = 'Enter :s to save or press enter to add another command'
SESSION_ADD_FILE = 'Enter a path to a file:'
SESSION_SHOULD_CONTINUE_FILE = 'Enter :s to save or press enter to add another file'
SAVE_CURRENT_SESSION = 'Enter a name to save the session:'
