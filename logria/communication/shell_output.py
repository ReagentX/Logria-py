import curses
import time
import re
from curses.textpad import Textbox, rectangle
import multiprocessing

from logria.communication import input_handler, keystrokes
from logria.interface import color_handler


class Logria():
    def __init__(self, q):
        self.q = q  # Qnput queue
        self.messages = []  # Message buffer

        # Handle when we are filtering
        self.matched_rows = []  # int array of matches when filtering is active
        self.last_index_searched = 0

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

        if self.func_handle is None:
            # Handle where the bottom of the stream is
            if self.stick_to_bottom:
                end = len(self.messages)
            elif self.stick_to_top:
                end = min(self.last_row, len(self.messages))
            elif self.manually_controlled_line:
                if len(self.messages) < self.last_row:
                    # If have fewer messages than lines, just render it all
                    end = len(self.messages)
                elif self.current_end < len(self.messages):
                    end = self.current_end
                else:
                    # If we have overscrolled, go back
                    if self.current_end > len(self.messages):
                        self.current_end = len(self.messages)
                    # Since current_end can be zero, we have to use the number of messages
                    end = len(self.messages)
            else:
                end = len(self.messages)

            self.current_end = end
            start = max(0, end - self.last_row - 1)
            # raise ValueError(start, end)
            for i in range(start, end):
                item = self.messages[i]
                # Subtract since we increment only if we write the row
                if current_row >= self.last_row - 2:
                    break
                current_row += 1
                # window.addstr(current_row, 2, item + '\n')
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
        elif self.matched_rows:
            # Handle where the bottom of the stream is
            if self.stick_to_bottom:
                end = len(self.matched_rows)
            elif self.stick_to_top:
                end = min(self.last_row, len(self.matched_rows))
            elif self.manually_controlled_line:
                if len(self.matched_rows) < self.last_row:
                    # If have fewer matched rows than lines, just render it all
                    end = len(self.matched_rows)
                elif self.current_end < len(self.matched_rows):
                    # If the current end is larger
                    end = self.current_end
                else:
                    # If we have overscrolled, go back
                    if self.current_end > len(self.matched_rows):
                        self.current_end = len(self.matched_rows)
                    # Since current_end can be zero, we have to use the number of matched rows
                    end = len(self.matched_rows)
            else:
                end = len(self.matched_rows)
            self.current_end = end
            start = max(0, end - self.last_row - 1)
            for i in range(start, end):
                messages_idx = self.matched_rows[i]
                item = self.messages[messages_idx]
                # Subtract since we increment only if we write the row
                if current_row >= self.last_row - 2:
                    break
                current_row += 1
                # window.addstr(current_row, 2, item + '\n')
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
        self.outwin.refresh()

    def process_matches(self) -> None:
        """
        Process the matches for filtering, should by async but the commented code here
        does not work

        # TODO: Fix this method
         [ ] Spawn a subprocess to find all the matches in the list of messages
        """
        # def add_to_list(result: multiprocessing.Queue, messages: list, last_idx_searched: int, func_handle: callable):
        #     """
        #     Main loop will create this separate process to find matches while the main loop runs
        #     """
        #     for index, message in range(last_idx_searched, len(messages)):
        #         print(index, message)
        #         if func_handle(message):
        #             result.put(index)
        #         return result

        # result = multiprocessing.Queue()
        # proc = multiprocessing.Process(target=add_to_list, args=(result, self.messages, self.last_index_searched, self.func_handle))
        # proc.start()
        # proc.join()
        # print('done')
        # self.last_index_searched = len(self.messages)
        # while not result.empty:
        #     idx = result.get()
        #     print(idx)
        #     self.matched_rows.append(idx)
        # self.write_to_prompt('in method')
        for index in range(self.last_index_searched, len(self.messages)):
            if self.func_handle(self.messages[index]):
                self.matched_rows.append(index)
        self.last_index_searched = len(self.messages)

    def regex_test_generator(self, pattern):
        return lambda string: bool(re.search(pattern, string))

    def write_to_prompt(self, string):
        """
        Used for command line and status line
        """
        self.reset_prompt()
        curses.curs_set(1)
        self.command_line.move(0, 0)
        self.command_line.addstr(0, 0, string)
        curses.curs_set(0)

    def reset_prompt(self):
        # Reset command prompt
        self.command_line.move(0, 0)
        self.command_line.deleteln()
        curses.curs_set(0)

    def activate_prompt(self):
        self.editing = True
        self.reset_prompt()
        curses.curs_set(1)
        self.box.edit(keystrokes.validator)

    def handle_command(self, command):
        self.reset_status()
        self.func_handle = self.regex_test_generator(command)
        # Tell the user what is happening since this is synchronous
        self.current_status = f'Searching buffer for regex /{command}/'
        self.write_to_prompt(self.current_status)
        self.process_matches()
        self.current_status = f'Regex with pattern /{command}/'
        self.write_to_prompt(self.current_status)
        self.render_text_in_output()
        curses.curs_set(0)

    def reset_status(self):
        self.current_status = 'No filter applied'
        self.func_handle = None
        self.matched_rows = []
        self.last_index_searched = 0
        self.current_end = 0
        self.stick_to_bottom = True
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
        self.last_row = output_height - output_start_row - 1  # The last row we can write to
        # The main output window
        self.outwin = curses.newwin(
            output_height, width - 1, output_start_row, 0)
        self.outwin.refresh()

        # Setup Command line
        # num_lines, num_cols, start_top, start_left
        self.command_line = curses.newwin(1, width, height - 2, 1)
        self.command_line.nodelay(True)
        # upper left:  (height - 2, 0)
        # lower right: (height, width)
        rectangle(stdscr, height - 3, 0, height - 1, width - 2)
        stdscr.refresh()
        self.box = Textbox(self.command_line)

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
                keypress = self.command_line.getkey()
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
                if self.func_handle:
                    self.process_matches()
                self.render_text_in_output()
