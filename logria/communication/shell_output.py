"""
Contains the main class that controls the state of the app
"""


import curses
import re
import time
from math import ceil
from curses.textpad import Textbox, rectangle
from os.path import isfile

from logria.communication.input_handler import (CommandInputStream,
                                                FileInputStream, InputStream)
from logria.interface import color_handler
from logria.logger.parser import Parser
from logria.utilities.command_parser import Resolver
from logria.utilities.constants import ANSI_COLOR_PATTERN
from logria.utilities.keystrokes import validator
from logria.utilities.regex_generator import regex_test_generator, get_real_length
from logria.utilities.session import SessionHandler


class Logria():
    """
    Main app class that controls the logical flow of the app
    """

    def __init__(self, stream: InputStream, poll_rate=0.005):
        # UI Elements initialized to None
        self.stdscr = None  # The entire window
        self.outwin: curses.window = None  # The output window
        self.command_line: curses.window = None  # The command line
        self.box: Textbox = None  # The text box inside the command line

        # App state
        self.poll_rate: float = poll_rate  # The rate at which we check for new messages
        self.height: int = None  # Window height
        self.width: int = None  # Window width
        self.prevous_render: list = None  # Store the state of the previous render so we know if we need to refresh
        # Pointer to the previous non-parsed message list, which is continuously updated
        self.previous_messages: list = []

        # Message buffers
        self.stderr_messages: list = []
        self.stdout_messages: list = []
        self.messages: list = self.stderr_messages  # Default to watching stderr

        # Regex Handler information
        self.func_handle: callable = None  # Regex func that handles filtering
        self.regex_pattern: str = ''  # Current regex pattern
        self.matched_rows: list = []  # Int array of matches when filtering is active
        self.last_index_regexed: int = 0  # The last index the filtering function saw

        # Processor information
        self.parser: Parser = None  # Reference to the current parser
        self.parser_index: int = 0  # Index for the parser to look at
        self.parsed_messages: list = []  # Array of parsed rows
        self.analytics_enabled: bool = False  # Array for statistics messages
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
        self.current_end: bool = 0  # Current last row we have rendered

        # If we do not have a stream yet, tell the user to set one up
        if stream is None:
            self.streams: list = []
        else:
            # Stream list to handle multiple streams
            self.streams: list = [stream]

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
                self.outwin.addstr(i, 0, '\n')
            except curses.error:
                pass
        # self.outwin.refresh()

    def setup_streams(self) -> None:
        """
        When launched without a stream, allow the user to define them for us
        """
        # Setup a SessionHandler and get the existing saved sessions
        session_handler = SessionHandler()
        # Tell the user what we are doing
        self.messages.append(
            'Enter a new command to open a stream or choose a saved one from the list:')
        self.messages.extend(session_handler.show_sessions())
        self.render_text_in_output()

        # Dump the existing status
        self.write_to_command_line('')

        # Create resolver class to resolve commands
        resolver = Resolver()

        # Get user input
        while True:
            time.sleep(self.poll_rate)
            self.activate_prompt()
            command = self.box.gather().strip()
            if not command:
                continue
            try:
                command = int(command)
                session = session_handler.load_session(command)
                commands = session.get('commands')
                # Commands need a type
                for command in commands:
                    if session.get('type') == 'file':
                        self.streams.append(FileInputStream(command))
                    elif session.get('type') == 'command':
                        self.streams.append(CommandInputStream(command))
            except ValueError:
                if isfile(command):
                    self.streams.append(
                        FileInputStream(command.split('/')))
                    session_handler.save_session(
                        'File: ' + command.replace('/', '|'), [command.split('/')], 'file')
                else:
                    cmd = resolver.resolve_command_as_list(command)
                    self.streams.append(CommandInputStream(cmd))
                    session_handler.save_session(
                        'Cmd: ' + command.replace('/', '|'), [cmd], 'command')
            break

        # Launch the subprocess
        for stream in self.streams:
            stream.start()

        # Set status back to what it was
        self.write_to_command_line(self.current_status)

        # Render immediately

        # Reset messages
        self.stderr_messages = []
        self.messages = self.stderr_messages

    def setup_parser(self):
        """
        Setup a parser object in the main runtime
        """
        # Reset the status for new writes
        self.reset_parser()
        self.reset_regex_status()

        # Store previous message pointer
        if self.messages is self.stderr_messages:
            self.previous_messages = self.stderr_messages
        elif self.messages is self.stdout_messages:
            self.previous_messages = self.stdout_messages

        # Stick to top to show options
        self.manually_controlled_line = False
        self.stick_to_bottom = False
        self.stick_to_top = True

        # Overwrite the messages pointer
        self.messages = Parser().show_patterns()
        self.render_text_in_output()
        while True:
            time.sleep(self.poll_rate)
            self.activate_prompt()
            command = self.box.gather().strip()
            if command == 'q':
                self.reset_parser()
                return
            else:
                try:
                    parser = Parser()
                    parser.load(Parser().patterns()[int(command)])
                    break
                except ValueError:
                    pass

        # Overwrite a different list this time, and reset it when done
        self.messages = parser.display_example()
        self.render_text_in_output()
        while True:
            time.sleep(self.poll_rate)
            self.activate_prompt()
            command = self.box.gather().strip()
            if command == 'q':
                self.reset_parser()
                return
            else:
                try:
                    command = int(command)
                    assert command < len(self.messages)
                    self.parser_index = int(command)
                    self.current_status = f'Parsing with {parser.get_name()}, field {command}'
                    self.write_to_command_line(self.current_status)
                    break
                except ValueError:
                    pass

        # Set parser
        self.parser = parser

        # Put pointer back to new array
        self.messages = self.parsed_messages

        # Render immediately

        # Stick to bottom again
        self.stick_to_bottom = True
        self.stick_to_top = False

    def reset_parser(self):
        """
        Remove the current parser, if any exists
        """
        if self.func_handle:
            self.current_status = f'Regex with pattern /{self.regex_pattern}/'
        else:
            self.current_status = 'No filter applied'  # CLI message, rendered after
        if self.previous_messages:
            # Move messages pointer to the previous state
            if self.previous_messages is self.stderr_messages:
                self.messages = self.stderr_messages
            else:
                self.messages = self.stdout_messages
            self.previous_messages = []
            self.parsed_messages = []  # Dump parsed messages
        self.parser = None  # Dump the parser
        self.parser_index = 0  # Dump the pattern index
        self.last_index_processed = 0  # Reset the last searched index
        self.current_end = 0  # We now do not know where to end
        self.stick_to_bottom = True  # Stay at the bottom for the next render
        self.write_to_command_line(self.current_status)

    def process_parser(self):
        """
        Load parsed messages to new array if we have matches

        # TODO: Same as process_matches
        """
        self.write_to_command_line('Handling message parsing...')
        for index in range(self.last_index_processed, len(self.previous_messages)):
            if self.analytics_enabled:
                self.parser.handle_analytics_for_message(
                    self.previous_messages[index])
                self.messages = self.parser.analytics_to_list()
                # For some reason this isn't switching back
                self.last_index_processed = len(self.previous_messages)
            else:
                if self.messages is not self.parsed_messages:
                    self.messages = self.parsed_messages
                match = self.parser.parse(self.previous_messages[index])
                if match:
                    try:
                        self.parsed_messages.append(match[self.parser_index])
                    except IndexError:
                        self.parsed_messages.append(
                            f'Error parsing! {self.previous_messages[index]}')
                self.last_index_processed = len(self.messages)
        self.write_to_command_line(self.current_status)

    def render_text_in_output(self) -> None:
        """
        Renders stream content in the output window

        If filters are inactive, we use `messages`. If they are active, we pull from `matched_rows`

        We write the whole message, regardless of length, because slicing a string allocates a new string
        """
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
                    # If we have over-scrolled, go back
                    if self.current_end > len(self.messages):
                        self.current_end = len(self.messages)
                    # Since current_end can be zero, we have to use the number of messages
                    end = len(self.messages)
            else:
                end = len(self.messages)
            self.current_end = end  # Save this row so we know where we are
            start = max(0, end - self.last_row - 1)
            # Don't do anything if nothing changed
            if self.prevous_render == self.messages[start:end]:
                return
            self.prevous_render = self.messages[start:end]
            self.clear_output_window()
            current_row = 0  # The row we are currently rendering
            for i in range(start, end):
                item = self.messages[i]
                # Instead of window.addstr, handle colors
                color_handler.addstr(self.outwin, current_row, 0, item.strip())
                current_row += ceil(get_real_length(item) / self.width) # Go to the next open line
                if current_row > self.last_row:
                    break
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
                    # If we have over-scrolled, go back
                    if self.current_end > len(self.matched_rows):
                        self.current_end = len(self.matched_rows)
                    # Since current_end can be zero, we have to use the number of matched rows
                    end = len(self.matched_rows)
            else:
                end = len(self.matched_rows)
            self.current_end = end
            start = max(0, end - self.last_row - 1)
            # Don't do anything if nothing changed
            if self.prevous_render == self.matched_rows[start:end]:
                return
            self.prevous_render = self.matched_rows[start:end]
            self.clear_output_window()
            current_row = 0  # The row we are currently rendering
            for i in range(start, end):
                messages_idx = self.matched_rows[i]
                item = self.messages[messages_idx]
                # Instead of window.addstr, handle colors, also handle regex highlighter
                if self.highlight_match:
                    # Remove all color codes
                    item = re.sub(ANSI_COLOR_PATTERN, '', item)
                    item = re.sub(
                        self.regex_pattern, f'\u001b[35m{self.regex_pattern}\u001b[0m', item.strip())
                # Print to current row, 2 chars from right edge
                color_handler.addstr(self.outwin, current_row, 0, item)
                current_row += ceil(get_real_length(item) / self.width) # Go to the next open line
                if current_row > self.last_row:
                    break
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
        self.write_to_command_line('Searching messages...')
        for index in range(self.last_index_regexed, len(self.messages)):
            if self.func_handle(self.messages[index]):
                self.matched_rows.append(index)
        self.last_index_regexed = len(self.messages)
        self.write_to_command_line(self.current_status)

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

    def handle_regex_command(self, command: str) -> None:
        """
        Handle a regex command
        """
        self.reset_regex_status()
        self.func_handle = regex_test_generator(command)
        self.highlight_match = True
        self.regex_pattern = command

        # Tell the user what is happening since this is synchronous
        self.current_status = f'Searching buffer for regex /{self.regex_pattern}/'
        self.write_to_command_line(self.current_status)

        # Process any new matched messages to render
        self.process_matches()

        # Tell the user we are now filtering
        self.current_status = f'Regex with pattern /{self.regex_pattern}/'
        self.write_to_command_line(self.current_status)

        # Render the text
        self.render_text_in_output()
        curses.curs_set(0)

    def reset_regex_status(self) -> None:
        """
        Reset current regex/filter status to no filter
        """
        if self.parser:
            self.current_status = f'Parsing with {self.parser.get_name()}, field {self.parser_index}'
        else:
            self.current_status = 'No filter applied'  # CLI message, rendered after
        self.prevous_render = None  # Reset previous render
        self.func_handle = None  # Disable filter
        self.highlight_match = False  # Disable highlighting
        self.regex_pattern = ''  # Clear the current pattern
        self.matched_rows = []  # Clear out matched rows
        self.last_index_regexed = 0  # Reset the last searched index
        self.current_end = 0  # We now do not know where to end
        self.stick_to_bottom = True  # Stay at the bottom for the next render
        self.write_to_command_line(self.current_status)  # Render status

    def handle_regex_mode(self) -> None:
        """
        Handle when user activates regex mode, including parsing textbox message
        """
        if not self.analytics_enabled:  # Disable regex in analytics view
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

    def handle_command_mode(self) -> None:
        """
        Handle when user activates command mode, including parsing textbox message
        """
        # Handle getting input from the command line for commands
        self.activate_prompt(':')
        command = self.box.gather().strip()
        curses.curs_set(0)
        if command:
            if command == ':q':
                for stream in self.streams:
                    stream.exit()
                return -1
            elif ':poll' in command:
                try:
                    command = float(command.replace(':poll', ''))
                    self.poll_rate = command
                    for stream in self.streams:
                        stream.poll_rate = command
                except ValueError:
                    pass
        self.reset_command_line()

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

        # Save these values
        self.height = height
        self.width = width

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
            if not self.streams:
                self.setup_streams()
            # Update messages from the input stream's queues, track time
            t_0 = time.perf_counter()
            for stream in self.streams:
                while not stream.stderr.empty():
                    message = stream.stderr.get()
                    self.stderr_messages.append(message)

                while not stream.stdout.empty():
                    message = stream.stdout.get()
                    self.stdout_messages.append(message)

            # Prevent this loop from taking up 100% of the CPU dedicated to the main thread by delaying loops
            t_1 = time.perf_counter() - t_0
            # Don't delay if the queue processing took too long
            time.sleep(max(0, self.poll_rate - t_1))

            try:
                keypress = self.command_line.getkey()  # Get keypress
                if keypress == '/':
                    self.handle_regex_mode()
                if keypress == ':':
                    result = self.handle_command_mode()
                    if result == -1:  # Handle exiting application loop
                        return result
                elif keypress == 'h':
                    self.prevous_render = None  #  Force render
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
                elif keypress == 's':
                    # Swap stdout and stderr
                    self.reset_parser()
                    self.reset_regex_status()
                    if self.messages is self.stderr_messages:
                        self.messages = self.stdout_messages
                    else:
                        self.messages = self.stderr_messages
                elif keypress == 'p':
                    # Enable parser
                    self.setup_parser()
                elif keypress == 'a':
                    # Enable analytics engine
                    if self.parser is not None:
                        self.last_index_processed = 0
                        if self.analytics_enabled:
                            self.current_status = f'Parsing with {self.parser.get_name()}, field {self.parser.get_analytics_for_index(self.parser_index)}'
                            self.parsed_messages = []
                            self.analytics_enabled = False
                        else:
                            self.analytics_enabled = True
                            self.current_status = f'Parsing with {self.parser.get_name()}, analytics view'
                elif keypress == 'z':
                    # Tear down parser
                    self.reset_parser()
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
                        len(self.messages) + 5, self.current_end + 1)
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
                if self.parser:
                    self.process_parser()  # This may block if there are a lot of messages
                if self.func_handle:
                    self.process_matches()  # This may block if there are a lot of messages
                self.render_text_in_output()
