"""
Contains the main class that controls the state of the app
"""


import curses
import re
import signal
import time
from math import ceil
from types import FrameType
from typing import Callable, List, Optional, Tuple, Union

from logria.commands.regex import reset_regex_status
from logria.communication.input_handler import InputStream
from logria.communication.render import determine_position
from logria.communication.setup import setup_streams
from logria.interface import color_handler
from logria.interface.textbox import Textbox, rectangle
from logria.logger.parser import Parser
from logria.logger.processor import process_matches, process_parser
from logria.utilities import constants
from logria.utilities.keystrokes import resolve_keypress, validator
from logria.utilities.regex_generator import get_real_length


class Logria():
    """
    Main app class that controls the logical flow of the app
    """

    def __init__(self, stream: Optional[InputStream], history_tape_cache: bool = True, smart_poll_rate: bool = True, poll_rate=0.001):
        # UI Elements initialized to None
        # The entire window
        self.stdscr: curses.window = None  # type: ignore
        # The entire window
        self.outwin: curses.window = None  # type: ignore
        # The command line
        self.command_line: curses.window = None  # type: ignore
        self.box: Textbox  # The text box inside the command line

        # App state passed as parameters
        # Wether we save command history
        self.history_tape_cache: bool = history_tape_cache
        self.poll_rate: float = poll_rate  # The rate at which we check for new messages
        self.smart_poll_rate: bool = smart_poll_rate

        # App state that changes as we use the app
        self.first_run: bool = True  # Whether this is a first run or not
        self.height: int = 0  # Window height
        self.width: int = 0  # Window width
        self.loop_time: float = 0  # How long a loop of the main app takes
        # Store the state of the previous render so we know if we need to refresh
        self.previous_render: Optional[Tuple[int, int]] = None
        # Pointer to the previous non-parsed message list, which is continuously updated
        self.previous_messages: List[str] = []
        self.exit_val = 0  # If exit_val is -1, the app dies

        # Message buffers
        self.stderr_messages: List[str] = []
        self.stdout_messages: List[str] = []
        # Default to watching stderr
        self.messages: List[str] = self.stderr_messages

        # Regex Handler information
        # Regex func that handles filtering
        self.func_handle: Optional[Callable] = None
        self.regex_pattern: str = ''  # Current regex pattern
        # List of matches when filtering is active
        self.matched_rows: List[int] = []
        self.last_index_regexed: int = 0  # The last index the filtering function saw

        # Processor information
        self.parser: Optional[Parser] = None  # Reference to the current parser
        self.parser_index: int = 0  # Index for the parser to look at
        self.parsed_messages: List[dict] = []  # List of parsed rows
        self.analytics_enabled: bool = False  # List for statistics messages
        self.last_index_processed: int = 0  # The last index the parsing function saw

        # Variables to store the current state of the app
        self.insert_mode: bool = False  # Default to insert mode (like vim) off
        self.current_status: str = ''  # Current status, aka what is in the command line
        # Determines whether we highlight the match to the user
        self.highlight_match: bool = True
        self.last_row: int = 0  # The last row we can render, aka number of lines
        self.stick_to_bottom: bool = True  # Whether we should follow the stream
        # Whether we should stick to the top and not render new lines
        self.stick_to_top: bool = False
        self.manually_controlled_line: bool = False  # Whether manual scroll is active
        self.current_end: int = 0  # Current last row we have rendered

        # If we do not have a stream yet, tell the user to set one up
        if stream is None:
            self.streams: List[InputStream] = []
        else:
            # Stream list to handle multiple streams
            self.streams = [stream]

    def build_command_line(self) -> None:
        """
        Creates a textbox object that represents the command line
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
        self.box = Textbox(
            self.command_line,
            insert_mode=self.insert_mode,
            poll_rate=self.poll_rate,
            history_cache=self.history_tape_cache)
        self.write_to_command_line(
            self.current_status)  # Update current status

    def render_text_in_output(self) -> None:
        """
        Renders stream content in the output window

        If filters are inactive, we use `messages`. If they are active, we pull from `matched_rows`

        We write the whole message, regardless of length, because slicing a string allocates a new string
        """
        # Store a pointer to the buffer of messages
        if self.func_handle is None:
            messages_pointer = self.messages
        else:
            # Ignore typing because we use different values depending on what this pointer is
            messages_pointer = self.matched_rows  # type: ignore

        # Determine the start and end position of the render
        start, end = determine_position(self, messages_pointer)
        # Don't do anything if nothing changed; start at index 0
        if not self.analytics_enabled and self.previous_render == (max(start, 0), end):
            return  # Early escape
        self.previous_render = (max(start, 0), end)
        self.outwin.erase()
        current_row = self.last_row  # The row we are currently rendering
        for i in range(end, start, -1):
            if messages_pointer is self.messages:
                # No processing needed for normal messages
                item = messages_pointer[i]
            elif messages_pointer is self.matched_rows:
                # Grab the matched message and optionally highlight it
                messages_idx = self.matched_rows[i]
                item = self.messages[messages_idx]
                if self.highlight_match:
                    # Remove all color codes before applying highlighter
                    item = re.sub(constants.ANSI_COLOR_PATTERN, '', item)
                    match = re.search(self.regex_pattern, item)
                    if match:
                        start, end = match.span()
                        matched_str = item[start:end]
                        item = item.replace(matched_str, f'\u001b[35m{matched_str}\u001b[0m')
            # Find the correct start position
            current_row -= ceil(get_real_length(item) / self.width)
            if current_row < 0:
                break
            # Instead of window.addstr, handle colors
            color_handler.addstr(self.outwin, current_row, 0, item.rstrip())
        self.outwin.refresh()

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

    def activate_prompt(self, text='') -> None:
        """
        Activate the prompt so we can edit it

        text: str, some text to prepend to the command
        """
        self.reset_command_line()
        if text:
            self.write_to_command_line(text)
        curses.curs_set(1)
        self.box.edit(validator)

    def update_poll_rate(self, new_poll_rate: float) -> None:
        """
        Update Logria's poll rate
        """
        self.poll_rate = new_poll_rate
        # Update stream poll rates
        for stream in self.streams:
            stream.poll_rate = new_poll_rate
        # Update command line poll rate
        self.box.poll_rate = new_poll_rate

    def handle_smart_poll_rate(self, t_1: float, new_messages: int) -> None:
        """
        Determine a reasonable poll rate based on the speed of messages received
        """
        if self.manually_controlled_line:
            pass
        elif self.smart_poll_rate:
            if not self.loop_time:
                self.loop_time = time.perf_counter()
            else:
                self.loop_time = t_1 - self.loop_time
                messages_per_second = new_messages / self.loop_time
                if messages_per_second > 0:
                    # Update poll rate
                    new_poll_rate = \
                        min(
                            max(
                                1 / messages_per_second,
                                constants.FASTEST_POLL_RATE
                            ),
                            constants.SLOWEST_POLL_RATE
                        )
                    self.update_poll_rate(new_poll_rate)

    def resize_window(self) -> None:
        """
        Resize curses elements when window size changes
        """
        self.height, self.width = self.stdscr.getmaxyx()
        curses.resizeterm(self.height, self.width)
        self.build_command_line()  # Rebuild the command line
        self.previous_render = None  # Force render
        self.render_text_in_output()

    def start(self) -> None:
        """
        Starts the program
        """
        signal.signal(signal.SIGINT, self.stop)  # type: ignore
        curses.wrapper(self.main)

    # pylint: disable=unused-argument
    def stop(self, signum: Optional[Union[str, int]] = None, frame: Optional[FrameType] = None) -> None:
        """
        Die if we send an exit signal of -1
        """
        for stream in self.streams:
            stream.exit()
        self.exit_val = -1
        # If we crash before the command line is set up:
        if getattr(self, 'box', None):
            self.box.stop()

    def main(self, stdscr) -> None:
        """
        Main program loop, handles user control and logical flow
        """
        curses.use_default_colors()
        self.stdscr = stdscr
        stdscr.keypad(1)
        height, width = stdscr.getmaxyx()  # Get screen size

        # Save these values
        self.height = height
        self.width = width - 1

        # Setup Output window
        output_start_row = 0  # Leave space for top border
        output_height = height - 3  # Leave space for command line
        self.last_row = output_height - output_start_row  # The last row we can write to
        # Create the window with these sizes
        self.outwin = curses.newwin(
            output_height, width - 1, output_start_row, 0)
        self.outwin.refresh()

        # Setup Command line
        self.build_command_line()

        # Update the command line status
        reset_regex_status(self)

        # Disable cursor:
        curses.curs_set(0)

        # Start the main app loop
        while True:
            if not self.streams:
                setup_streams(self)

            # Update messages from the input stream's queues, track time
            t_0 = time.perf_counter()
            new_messages: int = 0
            for stream in self.streams:
                while not stream.stderr.empty():
                    message = stream.stderr.get()
                    self.stderr_messages.append(message)
                    new_messages += 1

                while not stream.stdout.empty():
                    message = stream.stdout.get()
                    self.stdout_messages.append(message)
                    new_messages += 1
            # Prevent this loop from taking up 100% of the CPU dedicated to the main thread by delaying loops
            t_1 = time.perf_counter() - t_0
            # Don't delay if the queue processing took too long
            time.sleep(max(0, self.poll_rate - t_1))

            # Calculate new poll rate
            if self.smart_poll_rate:
                self.handle_smart_poll_rate(t_1, new_messages)

            # Since this is the first run, set the visible stream to the one that has the most messages
            if self.first_run and (len(self.stdout_messages) > 0 or len(self.stderr_messages) > 0):
                self.first_run = False
                # Default to stdout unless stderr has more messages
                if len(self.stdout_messages) >= len(self.stderr_messages):
                    self.messages = self.stdout_messages
                else:
                    self.messages = self.stderr_messages

            try:
                # Get keypress, raise curses.error if nothing detected
                keypress = self.command_line.getkey()
                resolve_keypress(self, keypress)
            except curses.error:
                if self.exit_val == -1:
                    return
                # If we have an active filter/parser, process it/them
                if self.parser:
                    # This may block if there are a lot of messages
                    process_parser(self)
                if self.func_handle:
                    # This may block if there are a lot of messages
                    process_matches(self)
                # Always try to render
                self.render_text_in_output()
