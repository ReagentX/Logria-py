"""
Extended stdlib textbox editing widget with Emacs-like keybindings and history tape

Adapted to work for a single line since we only use this for the Logria command line
"""
import curses
import curses.ascii
import time
from typing import Callable, Optional

from logria.communication.input_history import HistoryTape


def rectangle(win, uly, ulx, lry, lrx):
    """Draw a rectangle with corners at the provided upper-left
    and lower-right coordinates.
    """
    win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)


class Textbox():
    """Editing widget using the interior of a window object.
     Supports the following Emacs-like key bindings:

    Ctrl-A      Go to left edge of window.
    Ctrl-B      Cursor left, wrapping to previous line if appropriate.
    Ctrl-D      Delete character under cursor.
    Ctrl-E      Go to right edge (stripspaces off) or end of line (stripspaces on).
    Ctrl-F      Cursor right, wrapping to next line when appropriate.
    Ctrl-G      Terminate, returning the window contents.
    Ctrl-H      Delete character backward.
    Ctrl-J      Terminate if the window is 1 line, otherwise insert newline.
    Ctrl-K      If line is blank, delete it, otherwise clear to end of line.
    Ctrl-L      Refresh screen.
    Ctrl-O      Insert a blank line at cursor location.
    Ctrl-P      Scroll up history tape (like KEY_UP in the shell)
    Ctrl-N    Scroll down history tape (like KEY_DOWN in the shell)

    Move operations do nothing if the cursor is at an edge where the movement
    is not possible.  The following synonyms are supported where possible:

    KEY_LEFT = Ctrl-B, KEY_RIGHT = Ctrl-F, KEY_UP = Ctrl-P, KEY_DOWN = Ctrl-N
    KEY_BACKSPACE = Ctrl-h
    """

    def __init__(self, win, insert_mode: bool = False, poll_rate: float = 0.001, history_cache: bool = True):
        self.win = win
        self.insert_mode: bool = insert_mode
        self._update_max_yx()
        self.stripspaces = 1
        self.lastcmd: str = ''
        self.history_tape = HistoryTape(use_cache=history_cache)
        self.poll_rate: float = poll_rate
        self.exit_val: int = 0  # Exit exit() when set to -1
        win.keypad(1)

    def _update_max_yx(self):
        """
        Get the useable area of the textbox container
        """
        maxy, maxx = self.win.getmaxyx()
        self.maxy = maxy - 1
        self.maxx = maxx - 1

    def _end_of_line(self, y: int):
        """
        Go to the location of the first blank on the given line,
        returning the index of the last non-blank character.
        """
        self._update_max_yx()
        last = self.maxx
        while True:
            # pylint: disable=no-else-break
            if curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last+1)
                break
            elif last == 0:
                break
            last = last - 1
        return last

    def _insert_printable_char(self, ch: str):
        """
        Insert a character to the textbox
        """
        self._update_max_yx()
        (y, x) = self.win.getyx()
        backyx = None
        while y < self.maxy or x < self.maxx:
            if self.insert_mode:
                oldch = self.win.inch()
            # The try-catch ignores the error we trigger from some curses
            # versions by trying to write into the lowest-rightmost spot
            # in the window.
            try:
                self.win.addch(ch)
            except curses.error:
                pass
            if not self.insert_mode or not curses.ascii.isprint(oldch):
                break
            ch = oldch
            (y, x) = self.win.getyx()
            # Remember where to put the cursor back since we are in insert_mode
            if backyx is None:
                backyx = y, x

        if backyx is not None:
            self.win.move(*backyx)

    def do_command(self, ch: str):
        """
        Process a single editing command.
        """
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        if curses.ascii.isprint(ch):
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
        elif ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        elif ch in (curses.ascii.STX, curses.KEY_LEFT, curses.ascii.BS, curses.KEY_BACKSPACE):
            if x > 0:
                self.win.move(y, x-1)
            elif y == 0:
                pass
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
            else:
                self.win.move(y-1, self.maxx)
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
        elif ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
        elif ch == curses.ascii.ENQ:                           # ^e
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x < self.maxx:
                self.win.move(y, x+1)
            elif y == self.maxy:
                pass
            else:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0
            elif y < self.maxy:
                self.win.move(y+1, 0)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(0, 0)
                self.win.clrtoeol()
            new_cmd = self.history_tape.scroll_forward()
            # Write the new command from the tape to the command line
            for char in new_cmd:
                if curses.ascii.isprint(char):
                    if y < self.maxy or x < self.maxx:
                        self._insert_printable_char(char)
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(0, 0)
                self.win.clrtoeol()
            new_cmd = self.history_tape.scroll_back()
            # Write the new command from the tape to the command line
            for char in new_cmd:
                if curses.ascii.isprint(char):
                    if y < self.maxy or x < self.maxx:
                        self._insert_printable_char(char)
        return 1

    def gather(self) -> str:
        """
        Collect and return the contents of the window.
        """
        if self.exit_val == -1:
            return ':q'  # exit string
        result = ""
        self._update_max_yx()
        for y in range(self.maxy+1):
            self.win.move(y, 0)
            stop = self._end_of_line(y)
            if stop == 0 and self.stripspaces:
                continue
            for x in range(self.maxx+1):
                if self.stripspaces and x > stop:
                    break
                result = result + chr(curses.ascii.ascii(self.win.inch(y, x)))
            if self.maxy > 0:
                result = result + "\n"
        self.history_tape.add_item(result)
        return result

    def stop(self) -> None:
        """
        Die if we send exit signal
        """
        self.exit_val = -1

    def edit(self, validate: Optional[Callable] = None):
        """
        Edit in the widget window and collect the results.

        TODO: Async, not blocking
        """
        while True:
            if self.exit_val == -1:
                return ''
            time.sleep(self.poll_rate)
            ch = self.win.getch()
            if validate:
                ch = validate(ch)
            if not ch:
                continue
            if not self.do_command(ch):
                break
            self.win.refresh()
        return self.gather()
