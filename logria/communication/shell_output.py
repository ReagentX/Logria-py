"""
Contains the main class that controls the state of the app
"""


import curses
import time
import re
from curses.textpad import Textbox, rectangle
from multiprocessing import Queue

from logria.communication.input_handler import InputStream
from logria.interface import color_handler
from logria.utilities.keystrokes import validator
from logria.utilities.regex_generator import regex_test_generator
from logria.utilities.constants import ANSI_COLOR_PATTERN


class Logria():
    """
    Main app class that controls the logical flow of the app
    """

    def __init__(self, stream: InputStream):
        # UI Elements initialized to None
        self.stdscr = None  # The entire window
        self.outwin: curses.window = None  # The output window
        self.command_line: curses.window = None  # The command line
        self.box: Textbox = None  # The text box inside the command line

        # Data streams
        self.stderr_q: Queue = stream.stderr
        self.stdout_q: Queue = stream.stdout

        # Message buffers
        self.stderr_messages: list = []
        self.stdout_messages: list = []
        self.messages: Queue = self.stderr_messages  # Default to watching stderr

        # Processor information
        self.processor = None  # Reference to the current parser

        # Variables to store the current state of the app
        self.matched_rows: list = []  # Int array of matches when filtering is active
        self.last_index_searched: int = 0  # The last index the filtering function saw
        self.insert_mode: bool = False  # Default to insert mode (like vim) off
        self.current_status: str = ''  # Current status, aka what is in the command line
        self.regex_pattern: str = ''  # Current regex pattern
        self.func_handle: callable = None  # Regex func that handles filtering
        self.highlight_match: bool = True  # Determines whether we highlight the match to the user
        self.last_row: int = 0  # The last row we can render, aka number of lines
        self.editing: bool = False  # Whether we are currently editing the command
        self.stick_to_bottom: bool = True  # Whether we should follow the stream
        self.stick_to_top: bool = False  # Whether we should stick to the top and not render new lines
        self.manually_controlled_line: bool = False  # Whether manual scroll is active
        self.current_end: bool = 0  # Current last row we have rendered

    def build_command_line(self) -> None:
        """
        Creates a textbox object that has insert mode set to the passed value
        """
        if self.command_line:
            del self.command_line
        height, width = self.stdscr.getmaxyx()
        # 1 line, screen width, start 2 from the bottom, 1 char from the side
        self.command_line = curses.newwin(1, width, height - 2, 1)
        # Do not block the event loop waiting for input
        self.command_line.nodelay(True)
        # Draw rectangle around the command line
        # upper left:  (height - 2, 0), 2 chars up on left edge
        # lower right: (height, width), bottom right corner of screen
        rectangle(self.stdscr, height - 3, 0, height - 1, width - 2)
        self.stdscr.refresh()
        # Editable text box element
        self.box = Textbox(self.command_line, insert_mode=self.insert_mode)
        self.write_to_command_line(
            self.current_status)  # Update current status

    def clear_output_window(self) -> None:
        """
        Clears the text rendered in the output window
        """
        for i in range(self.last_row + 1):
            try:
                self.outwin.addstr(i, 2, '\n')
            except curses.error:
                pass

    def render_text_in_output(self) -> None:
        """
        Renders stream content in the output window

        If filters are inactive, we use `messages`. If they are active, we pull from `matched_rows`
        """
        self.clear_output_window()
        current_row = -1  # The row we are currently rendering

        # If filters are disabled
        if self.func_handle is None:
            # Handle where the bottom of the stream should be
            if self.stick_to_bottom:
                end = len(self.messages)
            elif self.stick_to_top:
                end = min(self.last_row + 1, len(self.messages))
            elif self.manually_controlled_line:
                if len(self.messages) < self.last_row:
                    # If have fewer messages than lines, just render it all
                    end = len(self.messages)
                elif self.current_end < self.last_row:
                    end = self.last_row
                elif self.current_end < len(self.messages):
                    # If we are looking at a valid line, render ends there
                    end = self.current_end
                else:
                    # If we have overscrolled, go back
                    if self.current_end > len(self.messages):
                        self.current_end = len(self.messages)
                    # Since current_end can be zero, we have to use the number of messages
                    end = len(self.messages)
            else:
                end = len(self.messages)
            self.current_end = end  # Save this row so we know where we are
            start = max(0, end - self.last_row - 1)
            for i in range(start, end):
                item = self.messages[i]
                # Subtract since we increment only if we write the row
                if current_row >= self.last_row:
                    break
                current_row += 1
                # Instead of window.addstr, handle colors
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
        elif self.matched_rows:
            # Handle where the bottom of the stream is
            if self.stick_to_bottom:
                end = len(self.matched_rows)
            elif self.stick_to_top:
                end = min(self.last_row + 1, len(self.matched_rows))
            elif self.manually_controlled_line:
                if len(self.matched_rows) < self.last_row:
                    # If have fewer matched rows than lines, just render it all
                    end = len(self.matched_rows)
                elif self.current_end < self.last_row:
                    end = self.last_row
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
                if current_row >= self.last_row:
                    break
                current_row += 1
                # Instead of window.addstr, handle colors, also handle regex highlighter
                if self.highlight_match:
                    # Remove all color codes
                    item = re.sub(ANSI_COLOR_PATTERN, '', item)
                    item = re.sub(
                        self.regex_pattern, f'\u001b[35m{self.regex_pattern}\u001b[0m', item)
                # Print to current row, 2 chars from right edge
                color_handler.addstr(self.outwin, current_row, 2, item + '\n')
        self.outwin.refresh()

    def process_matches(self) -> None:
        """
        Process the matches for filtering, should by async but the commented code here
        does not work

        # TODO: Fix this method
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

        # For each message, add its index to the list of matches; this is more efficient than
        # Storing a second copy of each match
        for index in range(self.last_index_searched, len(self.messages)):
            if self.func_handle(self.messages[index]):
                self.matched_rows.append(index)
        self.last_index_searched = len(self.messages)

    def write_to_command_line(self, string: str) -> None:
        """
        Writes a message to the command line
        """
        self.reset_command_line()
        curses.curs_set(1)
        self.command_line.move(0, 0)
        self.command_line.addstr(0, 0, string)
        curses.curs_set(0)

    def reset_command_line(self) -> None:
        """
        Resets the command line
        """
        self.command_line.move(0, 0)
        self.command_line.deleteln()
        curses.curs_set(0)

    def activate_prompt(self) -> None:
        """
        Activate the prompt so we can edit it
        """
        self.editing = True
        self.reset_command_line()
        curses.curs_set(1)
        self.box.edit(validator)

    def handle_regex_command(self, command: str) -> None:
        """
        Handle a regex command
        """
        self.reset_regex_status()
        self.func_handle = regex_test_generator(command)
        self.highlight_match = True
        self.regex_pattern = command

        # Tell the user what is happening since this is synchronous
        self.current_status = f'Searching buffer for regex /{command}/'
        self.write_to_command_line(self.current_status)

        # Process any new matched messages to render
        self.process_matches()

        # Tell the user we are now filtering
        self.current_status = f'Regex with pattern /{command}/'
        self.write_to_command_line(self.current_status)

        # Render the text
        self.render_text_in_output()
        curses.curs_set(0)

    def reset_regex_status(self) -> None:
        """
        Reset current regex/filter status to no filter
        """
        self.current_status = 'No filter applied'  # CLI message, renderd after
        self.func_handle = None  # Disable filter
        self.highlight_match = False  # Disable highlighting
        self.regex_pattern = ''  # Clear the current pattern
        self.matched_rows = []  # Clear out matched rows
        self.last_index_searched = 0  # Reset the last searched index
        self.current_end = 0  # We now do not know where to end
        self.stick_to_bottom = True  # Stay at the bottom for the next render
        self.write_to_command_line(self.current_status)  # Render status

    def start(self) -> None:
        """
        Starts the program
        """
        curses.wrapper(self.main)

    def main(self, stdscr) -> None:
        """
        Main program loop, handles user control and logical flow
        """
        curses.use_default_colors()
        self.stdscr = stdscr
        stdscr.keypad(1)
        height, width = stdscr.getmaxyx()  # Get screen size

        # Setup Output window
        output_start_row = 0  # Leave space for top border
        output_height = height - 3  # Leave space for command line
        self.last_row = output_height - output_start_row - \
            1  # The last row we can write to
        # Create the window with these sizes
        self.outwin = curses.newwin(
            output_height, width - 1, output_start_row, 0)
        self.outwin.refresh()

        # Setup Command line
        self.build_command_line()

        # Update the command line status
        self.reset_regex_status()

        # Disable cursor:
        curses.curs_set(0)

        # Start the main app loop
        while True:
            # Update messages from the input stream's queues, track time
            t_0 = time.perf_counter()
            while not self.stderr_q.empty():
                message = self.stderr_q.get()
                self.stderr_messages.append(message)
            while not self.stdout_q.empty():
                message = self.stdout_q.get()
                self.stdout_messages.append(message)

            # Prevent this loop from taking up 100% of the CPU dedicated to the main thread by delaying loops
            t_1 = time.perf_counter() - t_0
            # Don't delay if the queue processing took too long
            time.sleep(max(0, 0.001 - t_1))

            try:
                keypress = self.command_line.getkey()  # Get keypress
                if keypress == '/':
                    # Handle getting input from the command line for regex
                    self.activate_prompt()
                    command = self.box.gather().strip()
                    if command:
                        if command == ':q':
                            self.reset_regex_status()
                        else:
                            self.handle_regex_command(command)
                    else:
                        # If command is an empty string, ignore the input
                        self.reset_regex_status()
                        self.reset_command_line()
                elif keypress == 'h':
                    if self.func_handle and self.highlight_match:
                        self.highlight_match = False
                    elif self.func_handle and not self.highlight_match:
                        self.highlight_match = True
                    else:
                        self.highlight_match = False
                elif keypress == 'i':
                    # Toggle insert mode
                    if self.insert_mode:
                        self.insert_mode = False
                    else:
                        self.insert_mode = True
                    self.build_command_line()
                if keypress == 's':
                    self.reset_regex_status()
                    if self.messages == self.stderr_messages:
                        self.messages = self.stdout_messages
                    else:
                        self.messages = self.stderr_messages
                elif keypress == 'KEY_UP':
                    # Scroll up
                    self.manually_controlled_line = True
                    self.stick_to_top = False
                    self.stick_to_bottom = False
                    self.current_end = max(0, self.current_end - 1)
                elif keypress == 'KEY_DOWN':
                    # Scroll down
                    self.manually_controlled_line = True
                    self.stick_to_top = False
                    self.stick_to_bottom = False
                    self.current_end = min(
                        len(self.messages), self.current_end + 1)
                elif keypress == 'KEY_RIGHT':
                    # Stick to bottom
                    self.stick_to_top = False
                    self.stick_to_bottom = True
                    self.manually_controlled_line = False
                elif keypress == 'KEY_LEFT':
                    # Stick to top
                    self.stick_to_top = True
                    self.stick_to_bottom = False
                    self.manually_controlled_line = False
            except curses.error:
                # If we have an active filter, process it, always render
                if self.func_handle:
                    self.process_matches()  # This may block if there are a lot of messages
                self.render_text_in_output()
