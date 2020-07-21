"""
Handles parsing color escape code sequences in logs to the relevant curses
colors so that we do not get ugly strings like `033[94m Blue`

Adapted from https://github.com/spellr/culour/blob/master/culour/culour.py
"""

import os
import curses
from typing import Dict, Tuple

COLOR_PAIRS_CACHE: Dict[Tuple[int, int], int] = {}
DEFAULT_COLOR = -1


class TerminalColors():
    """
    Dataclass to store the replacement colors
    """
    WHITE = '[37'
    CYAN = '[36'
    MAGENTA = '[35'
    BLUE = '[34'
    GREEN = '[32'
    YELLOW = '[33'
    RED = '[31'
    BLACK = '[30'
    BRIGHT_WHITE = '[97'
    BRIGHT_CYAN = '[96'
    BRIGHT_MAGENTA = '[95'
    BRIGHT_BLUE = '[94'
    BRIGHT_GREEN = '[92'
    BRIGHT_YELLOW = '[93'
    BRIGHT_RED = '[91'
    BRIGHT_BLACK = '[97'
    END = '[0'
    DEFAULT_FOREGROUND = '[39'
    DEFAULT_BACKGROUND = '[49'


TERMINAL_COLOR_TO_CURSES = {
    TerminalColors.WHITE: curses.COLOR_WHITE,
    TerminalColors.CYAN: curses.COLOR_CYAN,
    TerminalColors.MAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.BLUE: curses.COLOR_BLUE,
    TerminalColors.GREEN: curses.COLOR_GREEN,
    TerminalColors.YELLOW: curses.COLOR_YELLOW,
    TerminalColors.RED: curses.COLOR_RED,
    TerminalColors.BLACK: curses.COLOR_BLACK,
    TerminalColors.BRIGHT_WHITE: curses.COLOR_WHITE,
    TerminalColors.BRIGHT_CYAN: curses.COLOR_CYAN,
    TerminalColors.BRIGHT_MAGENTA: curses.COLOR_MAGENTA,
    TerminalColors.BRIGHT_BLUE: curses.COLOR_BLUE,
    TerminalColors.BRIGHT_GREEN: curses.COLOR_GREEN,
    TerminalColors.BRIGHT_YELLOW: curses.COLOR_YELLOW,
    TerminalColors.BRIGHT_RED: curses.COLOR_RED,
    TerminalColors.BRIGHT_BLACK: curses.COLOR_BLACK,
    TerminalColors.END: DEFAULT_COLOR,
    TerminalColors.DEFAULT_FOREGROUND: DEFAULT_COLOR,
    TerminalColors.DEFAULT_BACKGROUND: DEFAULT_COLOR
}


def _get_color(foreground: int, background: int):
    key = (foreground, background)
    if key not in COLOR_PAIRS_CACHE:
        # Use the pairs from 101 and after, so there's less chance they'll be overwritten by the user
        pair_num = len(COLOR_PAIRS_CACHE) + 101
        curses.init_pair(pair_num, foreground, background)
        COLOR_PAIRS_CACHE[key] = pair_num

    return COLOR_PAIRS_CACHE[key]


def _color_str_to_color_pair(color: str):
    if color == TerminalColors.END:
        foreground = DEFAULT_COLOR
    else:
        try:
            foreground = TERMINAL_COLOR_TO_CURSES[color]
        except KeyError:
            raise ValueError(f'`{color}` not loaded to colors!')
    color_pair = _get_color(foreground, DEFAULT_COLOR)
    return color_pair


def _sanitize(line: str) -> str:
    """
    Sanitize null bytes from strings before we try and render them
    """
    if '\x00' in line:
        line = line.replace('\x00', '')
    return line


def _add_line(y_coord: int, x_coord: int, window, line: str):
    # Sanitize string
    line = _sanitize(line)
    # split but \033 which stands for a color change
    color_split = line.split('\033')

    # Print the first part of the line without color change
    default_color_pair = _get_color(DEFAULT_COLOR, DEFAULT_COLOR)
    try:
        window.addstr(y_coord, x_coord, color_split[0], curses.color_pair(default_color_pair))
        window.noutrefresh()
        y_coord, x_coord = curses.getsyx()
    except curses.error:
        pass

    # Iterate over the rest of the line-parts and print them with their colors
    for substring in color_split[1:]:
        color_str = substring.split('m')[0]
        substring = substring[len(color_str)+1:]
        color_pair = _color_str_to_color_pair(color_str)
        try:
            window.addstr(y_coord, x_coord, substring, curses.color_pair(color_pair))
            window.noutrefresh()
            y_coord, x_coord = curses.getsyx()
        except curses.error:
            pass


def _inner_addstr(window, string: str, y_coord=-1, x_coord=-1):
    assert curses.has_colors(
    ), "Curses wasn't configured to support colors. Call curses.start_color()"

    cur_y, cur_x = window.getyx()
    if y_coord == -1:
        y_coord = cur_y
    if x_coord == -1:
        x_coord = cur_x
    for line in string.split(os.linesep):
        _add_line(y_coord, x_coord, window, line)
        # next line
        y_coord += 1


def addstr(*args):
    """
    Adds the color-formatted string to the given window, in the given coordinates
    To add in the current location, call like this:
        addstr(window, string)
    and to set the location to print the string, call with:
        addstr(window, y, x, string)
    Only use color pairs up to 100 when using this function,
    otherwise you will overwrite the pairs used by this function
    """
    if len(args) != 2 and len(args) != 4:
        raise TypeError("addstr requires 2 or 4 arguments")

    if len(args) == 4:
        window = args[0]
        y_coord = args[1]
        x_coord = args[2]
        string = args[3]
    else:
        window = args[0]
        string = args[1]
        y_coord = -1
        x_coord = -1

    return _inner_addstr(window, string, y_coord, x_coord)
