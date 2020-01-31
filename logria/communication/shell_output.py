import curses
import time
import re
from curses.textpad import Textbox, rectangle

from logria.communication import input_handler, keystrokes
from logria.interface import color_handler


class Logria():
    def __init__(self, q):
        self.q = q
        self.messages = []
        self.matched_rows = []
        self.current_status = ''
        # Handle for the processing func to check with when rendering output
        self.func_handle = None
        self.last_row = None
        self.editing = False
        self.manually_controlled_line = False
        self.stick_to_top = False
        self.stick_to_bottom = True
        self.current_end = 0

    def clear_output_window(self):
        # clear the window
        for i in range(self.last_row):
            self.outwin.addstr(i, 2, '\n')

    def render_text_in_output(self):
        self.clear_output_window()
        current_row = 0

        # Handle where the bottom of the stream is
        if self.stick_to_bottom:
            end = len(self.messages)
        elif self.stick_to_top:
            end = min(self.last_row, len(self.messages))
        elif self.manually_controlled_line:
            end = self.current_end
        else:
            end = len(self.messages)

        """
        If we are currently filtereing:

        - use `matched_rows`
        - when we find a match, copy that index to the new list
        - use the new list to paginate when rendering,
          accessing those indexes in the main list
        """

        self.current_end = end
        start = max(0, end - self.last_row - 1)
        # raise ValueError(start, end)
        for i in range(start, end):
            item = self.messages[i]
            # Subtract since we increment only if we write the row
            if current_row >= self.last_row - 2:
                break
            if self.func_handle is None:
                current_row += 1
                # window.addstr(current_row, 2, item + '\n')
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
            elif self.func_handle(item):
                current_row += 1
                # window.addstr(current_row, 2, item + '\n')
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
        self.outwin.refresh()

    def regex_test_generator(self, pattern):
        return lambda string: bool(re.search(pattern, string))

    def write_to_prompt(self, string):
        """
        Used for command line and status line
        """
        curses.curs_set(1)
        self.editwin.move(0, 0)
        self.editwin.addstr(0, 0, string)
        curses.curs_set(0)

    def reset_prompt(self):
        # Reset command prompt
        self.editwin.move(0, 0)
        self.editwin.deleteln()
        curses.curs_set(0)

    def activate_prompt(self):
        self.editing = True
        self.reset_prompt()
        curses.curs_set(1)
        self.box.edit(keystrokes.validator)

    def handle_command(self, command):
        self.editing = False
        self.reset_prompt()
        self.current_status = f'Regex with pattern /{command}/'
        self.write_to_prompt(self.current_status)
        self.func_handle = self.regex_test_generator(command)
        self.render_text_in_output()
        curses.curs_set(0)

    def reset_status(self):
        self.reset_prompt()
        self.current_status = 'No filter applied'
        self.func_handle = None
        self.write_to_prompt(self.current_status)

    def start(self):
        curses.wrapper(self.main, self.q)

    def main(self, stdscr, q):
        # self.stdscr = stdscr
        self.q = q
        # stdscr.nodelay(True)
        stdscr.keypad(1)
        height, width = stdscr.getmaxyx()

        # Setup Output window
        output_start_row = 0  # Leave space for top border
        output_height = height - 2  # Leave space for command line
        self.last_row = output_height - output_start_row - 1
        self.outwin = curses.newwin(
            output_height, width - 1, output_start_row, 0)
        self.outwin.refresh()

        # Seetup Command line
        # num_lines, num_cols, start_top, start_left
        self.editwin = curses.newwin(1, width, height - 2, 1)
        self.editwin.nodelay(True)
        # upper left:  (height - 2, 0)
        # lower right: (height, width)
        rectangle(stdscr, height - 3, 0, height - 1, width - 2)
        stdscr.refresh()
        self.box = Textbox(self.editwin)

        # Update the status
        self.reset_status()

        # Disable cursor:
        curses.curs_set(0)
        self.stdscr = stdscr
        while True:
            # Prevent this loop from taking up 100% of the CPU dedicated to the main thread
            time.sleep(0.001)

            # Update from the queue
            while not self.q.empty():
                message = self.q.get()
                self.messages.append(message)

            try:
                keypress = self.editwin.getkey()
                if keypress == ':':
                    self.activate_prompt()
                    command = self.box.gather().strip()
                    if command:
                        if command == ':q':
                            self.reset_status()
                        else:
                            self.handle_command(command)
                elif keypress == 'KEY_UP':
                    self.manually_controlled_line = True
                    self.stick_to_top = False
                    self.stick_to_bottom = False
                    self.current_end = max(0, self.current_end - 1)
                elif keypress == 'KEY_DOWN':
                    self.manually_controlled_line = True
                    self.stick_to_top = False
                    self.stick_to_bottom = False
                    self.current_end = min(
                        len(self.messages), self.current_end + 1)
                elif keypress == 'KEY_RIGHT':
                    self.stick_to_top = False
                    self.stick_to_bottom = True
                    self.manually_controlled_line = False
                elif keypress == 'KEY_LEFT':
                    self.stick_to_top = True
                    self.stick_to_bottom = False
                    self.manually_controlled_line = False
            except:
                self.render_text_in_output()
