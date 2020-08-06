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


# Source: https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
FOREGROUND = {
    # Normal
    '[37': curses.COLOR_WHITE,
    '[36': curses.COLOR_CYAN,
    '[35': curses.COLOR_MAGENTA,
    '[34': curses.COLOR_BLUE,
    '[33': curses.COLOR_YELLOW,
    '[32': curses.COLOR_GREEN,
    '[31': curses.COLOR_RED,
    '[30': curses.COLOR_BLACK,
    # Bright
    '[97': curses.COLOR_WHITE,
    '[96': curses.COLOR_CYAN,
    '[95': curses.COLOR_MAGENTA,
    '[94': curses.COLOR_BLUE,
    '[93': curses.COLOR_YELLOW,
    '[92': curses.COLOR_GREEN,
    '[91': curses.COLOR_RED,
    '[90': curses.COLOR_BLACK,
}
BACKGROUND = {
    # Normal
    '[47': curses.COLOR_WHITE,
    '[46': curses.COLOR_CYAN,
    '[45': curses.COLOR_MAGENTA,
    '[44': curses.COLOR_BLUE,
    '[43': curses.COLOR_YELLOW,
    '[42': curses.COLOR_GREEN,
    '[41': curses.COLOR_RED,
    '[40': curses.COLOR_BLACK,
    # Bright
    '[107': curses.COLOR_WHITE,
    '[106': curses.COLOR_CYAN,
    '[105': curses.COLOR_MAGENTA,
    '[104': curses.COLOR_BLUE,
    '[103': curses.COLOR_YELLOW,
    '[102': curses.COLOR_GREEN,
    '[101': curses.COLOR_RED,
    '[100': curses.COLOR_BLACK,
}


def _get_color(foreground: int, background: int):
    """
    Memoize init_pair wrapper; store an index of previously used color combinations

    init_color creates an integer and stores it as the primary key to a color pair,
    so here we cache the results so we do not overwrite old pairs
    """
    key = (foreground, background)
    if key not in COLOR_PAIRS_CACHE:
        # Use the pairs from 101 and after, so there's less chance they'll be overwritten by the user
        pair_num = len(COLOR_PAIRS_CACHE) + 101
        try:
            curses.init_pair(pair_num, foreground, background)
        except curses.error:
            # If colors were never enabled, this call does not matter anyway
            pass
        COLOR_PAIRS_CACHE[key] = pair_num

    return COLOR_PAIRS_CACHE[key]


def _color_str_to_color_pair(color: str):
    """
    Convert the escape code color to the curses color binding
    """
    foreground = FOREGROUND.get(color, DEFAULT_COLOR)
    background = BACKGROUND.get(color, DEFAULT_COLOR)
    color_pair = _get_color(foreground, background)
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
        window.addstr(y_coord, x_coord,
                      color_split[0], curses.color_pair(default_color_pair))
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
            window.addstr(y_coord, x_coord, substring,
                          curses.color_pair(color_pair))
            window.noutrefresh()
            y_coord, x_coord = curses.getsyx()
        except curses.error:
            pass


def _inner_addstr(window, string: str, y_coord=-1, x_coord=-1):
    if not curses.has_colors:
        raise ValueError(
            'Curses was not configured to support colors. Call `curses.start_color()`')

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
