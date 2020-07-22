"""
Utilities to handle input validation
"""


from typing import Callable, Dict

from logria.commands import command, edit, parser, regex, scroll, window

STROKES: Dict[str, Callable] = {
    '/': regex.handle_regex,
    'h': regex.toggle_highlight,
    ':': command.handle_command,
    'i': edit.toggle_insert_mode,
    's': window.swap_input,
    'p': parser.enable_parser,
    'a': parser.enable_analytics,
    'z': parser.teardown_parser,
    'KEY_RESIZE': window.resize,
    'KEY_UP': scroll.up,
    'KEY_DOWN': scroll.down,
    'KEY_PPAGE': scroll.pgup,
    'KEY_NPAGE': scroll.pgdn,
    'KEY_RIGHT': scroll.bottom,
    'KEY_LEFT': scroll.top,
}


def resolve_keypress(logria: 'Logria', key_press: str) -> None:  # type: ignore
    """
    Resolve a key press to a callable in the dictionary
    """
    if key_press in STROKES:
        STROKES[key_press](logria)


def validator(key: int):
    """
    Intercept invalid strokes and convert them to valid ones
    """
    # Handle backspace on MacOS
    if key == 127:
        return 263  # Ctrl-h
    return key
