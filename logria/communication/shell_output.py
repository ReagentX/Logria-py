"""
Contains the main class that controls the state of the app
"""


import curses
import re
import time
from curses.textpad import Textbox, rectangle
from json import JSONDecodeError
from math import ceil
from os.path import isfile
from typing import List

from logria.communication.input_handler import (CommandInputStream,
                                                FileInputStream, InputStream)
from logria.interface import color_handler
from logria.logger.parser import Parser
from logria.utilities import constants
from logria.utilities.command_parser import Resolver
from logria.utilities.keystrokes import validator
from logria.utilities.regex_generator import (get_real_length,
                                              regex_test_generator)
from logria.utilities.session import SessionHandler


class Logria():
    """
    Main app class that controls the logical flow of the app
    """

    def __init__(self, stream: InputStream, poll_rate=0.001):
        # UI Elements initialized to None
        self.stdscr = None  # The entire window
        self.outwin: curses.window = None  # The output window
        self.command_line: curses.window = None  # The command line
        self.box: Textbox = None  # The text box inside the command line

        # App state
        self.poll_rate: float = poll_rate  # The rate at which we check for new messages
        self.height: int = None  # Window height
        self.width: int = None  # Window width
        # Store the state of the previous render so we know if we need to refresh
        self.previous_render: List[str] = None
        # Pointer to the previous non-parsed message list, which is continuously updated
        self.previous_messages: List[str] = []
        self.exit_val = 0  # If exit_val is -1, the app dies

        # Message buffers
        self.stderr_messages: List[str] = []
        self.stdout_messages: List[str] = []
        self.messages: list = self.stderr_messages  # Default to watching stderr

        # Regex Handler information
        self.func_handle: callable = None  # Regex func that handles filtering
        self.regex_pattern: str = ''  # Current regex pattern
        # Int array of matches when filtering is active
        self.matched_rows: List[int] = []
        self.last_index_regexed: int = 0  # The last index the filtering function saw

        # Processor information
        self.parser: Parser = None  # Reference to the current parser
        self.parser_index: int = 0  # Index for the parser to look at
        self.parsed_messages: List[dict] = []  # Array of parsed rows
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
            self.streams: List[InputStream] = []
        else:
            # Stream list to handle multiple streams
            self.streams: List[InputStream] = [stream]

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

    def setup_streams(self) -> None:
        """
        When launched without a stream, allow the user to define them for us
        """
        # Setup a SessionHandler and get the existing saved sessions
        session_handler = SessionHandler()
        # Tell the user what we are doing
        self.messages.extend(constants.START_MESSAGE)
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
                if not session:
                    continue
                commands = session.get('commands')
                # Commands need a type
                for command in commands:
                    if session.get('type') == 'file':
                        self.streams.append(FileInputStream(command))
                    elif session.get('type') == 'command':
                        self.streams.append(CommandInputStream(command))
            except JSONDecodeError as err:
                self.messages.append(
                    f'Invalid JSON: {err.msg} on line {err.lineno}, char {err.colno}')
                self.render_text_in_output()
                continue
            except ValueError:
                if command == ':config':
                    self.config_mode()
                    return
                elif command == ':q':
                    self.stop()
                elif isfile(command):
                    self.streams.append(
                        FileInputStream(command.split('/')))
                    session_handler.save_session(
                        'File - ' + command.replace('/', '|'), [command.split('/')], 'file')
                else:
                    cmd = resolver.resolve_command_as_list(command)
                    self.streams.append(CommandInputStream(cmd))
                    session_handler.save_session(
                        'Cmd - ' + command.replace('/', '|'), [cmd], 'command')
            break

        # Launch the subprocess
        for stream in self.streams:
            stream.poll_rate = self.poll_rate
            stream.start()

        # Set status back to what it was
        self.write_to_command_line(self.current_status)

        # Render immediately
        self.previous_render = None

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
        self.stick_to_bottom = True
        self.stick_to_top = False

        # Overwrite the messages pointer
        self.messages = Parser().show_patterns()
        self.previous_render = None
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
                except JSONDecodeError as err:
                    self.messages.append(
                        f'Invalid JSON: {err.msg} on line {err.lineno}, char {err.colno}')
                except ValueError:
                    pass

        # Overwrite a different list this time, and reset it when done
        self.messages = parser.display_example()
        self.previous_render = None
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
                    self.current_status = f'Parsing with {parser.get_name()}, field {parser.get_analytics_for_index(command)}'
                    self.write_to_command_line(self.current_status)
                    break
                except ValueError:
                    pass
                except AssertionError:
                    pass

        # Set parser
        self.parser = parser

        # Put pointer back to new array
        self.messages = self.parsed_messages

        # Render immediately
        self.previous_render = None

        # Stick to bottom again
        self.last_index_processed = 0
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
        self.analytics_enabled = False  # Disable analytics blocker
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
                        # If there was an error parsing, the message did not match the current pattern
                        pass
                self.last_index_processed = len(self.messages)

    def determine_render_position(self, messages_pointer: List[str]) -> (int, int):
        """
        Determine the start and end positions for a screen render
        """
        if self.stick_to_top:
            end = 0
            rows = 0
            for i in messages_pointer:
                if messages_pointer is self.messages:
                    # No processing needed for normal messages
                    item = i
                elif messages_pointer is self.matched_rows:
                    # Grab the matched message
                    item = self.messages[i]
                # Determine if the message will fit in the window
                msg_lines = ceil(get_real_length(item) / self.width)
                rows += msg_lines
                # If we can fit, increment the last row number
                if rows < self.last_row and end < len(messages_pointer) - 1:
                    end += 1
                else:
                    break
            self.current_end = end  # Save this row so we know where we are
            # When iterating backwards, we need to end at 0, so we must create a range
            # object like range(10, -1, -1) to generate a list that ends at 0
            # If there are no messages, we want to not iterate later, so we change the
            # -1 to 0 so that we do not iterate at all
            return -1 if messages_pointer else 0, end  # Early escape
        elif self.stick_to_bottom:
            end = len(messages_pointer) - 1
        elif self.manually_controlled_line:
            if len(messages_pointer) < self.last_row:
                # If have fewer messages than lines, just render it all
                end = len(messages_pointer) - 1
            elif self.current_end < self.last_row:
                # If the last row we rendered comes before the last row we can render,
                # use all of the available rows
                end = self.current_end
            elif self.current_end < len(messages_pointer):
                # If we are looking at a valid line, render ends there
                end = self.current_end
            else:
                # If we have over-scrolled, go back
                if self.current_end > len(messages_pointer):
                    self.current_end = len(messages_pointer)
                # Since current_end can be zero, we have to use the number of messages
                end = len(messages_pointer)
        else:
            end = len(messages_pointer)
        self.current_end = end  # Save this row so we know where we are
        # Last index of a list is length - 1
        start = max(-1, end - self.last_row - 1)
        return start, end

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
            messages_pointer = self.matched_rows

        # Determine the start and end position of the render
        start, end = self.determine_render_position(messages_pointer)
        # Don't do anything if nothing changed; start at index 0
        if self.previous_render == messages_pointer[max(start, 0):end]:
            return
        self.previous_render = messages_pointer[max(start, 0):end]
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
                    item = re.sub(
                        self.regex_pattern, f'\u001b[35m{self.regex_pattern}\u001b[0m', item.rstrip())
            # Find the correct start position
            current_row -= ceil(get_real_length(item) / self.width)
            if current_row < 0:
                break
            # Instead of window.addstr, handle colors
            color_handler.addstr(self.outwin, current_row, 0, item.rstrip())
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
        for index in range(self.last_index_regexed, len(self.messages)):
            if self.func_handle(self.messages[index]):
                self.matched_rows.append(index)
        self.last_index_regexed = len(self.messages)

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
        self.previous_render = None  # Reset previous render
        self.func_handle = None  # Disable filter
        self.highlight_match = False  # Disable highlighting
        self.regex_pattern = ''  # Clear the current pattern
        self.matched_rows = []  # Clear out matched rows
        self.last_index_regexed = 0  # Reset the last searched index
        self.current_end = 0  # We now do not know where to end
        self.stick_to_bottom = True  # Stay at the bottom for the next render
        self.write_to_command_line(self.current_status)  # Render status

    def handle_create_session_file(self, session: SessionHandler) -> bool:
        cmd_resolver = Resolver()  # The resolver we use to add commands

        self.messages.append(constants.SESSION_ADD_FILE)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        session.set_type('file')
        self.activate_prompt()
        file_path = self.box.gather().strip()
        file_path = cmd_resolver.resolve_file_as_list(file_path)
        if isfile('/'.join(file_path)):
            session.add_command(file_path)
            self.messages = session.as_list()
            self.messages.append(constants.SESSION_SHOULD_CONTINUE_FILE)
            self.previous_render = None  # Force render
            self.render_text_in_output()
            self.activate_prompt()
            user_done = self.box.gather().strip()
            if user_done == ':s':
                self.messages = [constants.SAVE_CURRENT_SESSION]
                self.previous_render = None  # Force render
                self.render_text_in_output()
                self.activate_prompt()
                filename = self.box.gather().strip()
                session.save_current_session(filename)
                return True
        elif file_path == ':q':
            self.stop()
        else:
            self.messages.append(f'Cannot resolve path: {"/".join(file_path)}')
            self.previous_render = None  # Force render
            self.render_text_in_output()
        return False

    def handle_create_session_command(self, session: SessionHandler) -> bool:
        cmd_resolver = Resolver()  # The resolver we use to add commands
        self.messages.append(constants.SESSION_ADD_COMMAND)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        session.set_type('command')
        self.activate_prompt()
        command = self.box.gather().strip()
        command = cmd_resolver.resolve_command_as_list(command)
        session.add_command(command)
        self.messages = session.as_list()
        self.messages.append(constants.SESSION_SHOULD_CONTINUE_COMMAND)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        self.activate_prompt()
        user_done = self.box.gather().strip()
        if user_done == ':s':
            self.messages = [constants.SAVE_CURRENT_SESSION]
            self.previous_render = None  # Force render
            self.render_text_in_output()
            self.activate_prompt()
            filename = self.box.gather().strip()
            session.save_current_session(filename)
            return True
        elif command == ':q':
            self.stop()
        return False

    def handle_create_session(self) -> None:
        """
        Handle the creation of new sessions
        """
        # Render text
        self.current_end = 0
        self.messages = constants.CREATE_SESSION_START_MESSAGES
        self.previous_render = None  # Force render
        self.render_text_in_output()

        # Get the user choice
        choice = None
        while choice not in {'file', 'command'}:
            self.activate_prompt()
            choice = self.box.gather().strip()
            if choice == ':q':
                self.stop()
                break

        done = False
        self.messages = []
        temp_session = SessionHandler()  # The session object we build
        while not done:
            if choice == 'file':
                done = self.handle_create_session_file(temp_session)
            elif choice == 'command':
                done = self.handle_create_session_command(temp_session)
            elif choice == ':q':
                self.stop()
                break
            else:
                raise ValueError(f'{choice} not one of ("file", "command")')
        self.setup_streams()

    def handle_create_parser(self) -> None:
        temp_parser = Parser()

        # Render text
        self.current_end = 0
        self.messages = constants.CREATE_PARSER_MESSAGES
        self.previous_render = None  # Force render
        self.render_text_in_output()
        # Get type
        self.activate_prompt()
        parser_type = None
        while parser_type not in {'regex', 'split'}:
            self.activate_prompt()
            parser_type = self.box.gather().strip()

        # Handle next step
        self.messages = [f'Parser type {parser_type}']
        self.messages.append(constants.PARSER_SET_NAME)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        # Get name
        self.activate_prompt()
        parser_name = self.box.gather().strip()

        # Handle next step
        self.messages.append(f'Parser name {parser_name}')
        self.messages.append(constants.PARSER_SET_EXAMPLE)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        # Get example
        self.activate_prompt()
        parser_example = self.box.gather().strip()

        # Handle next step
        self.messages.append(f'Parser example {parser_example}')
        self.messages.append(constants.PARSER_SET_PATTERN)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        # Get pattern
        self.activate_prompt()
        parser_pattern = self.box.gather()

        # Set the parser's data
        temp_parser.set_pattern(
            parser_pattern, parser_type, parser_name, parser_example, {})

        # Determine the analytics dict
        parts = temp_parser.parse(parser_example)
        analytics = {part: 'count' for part in parts}

        # Set the parser's data with analytics
        temp_parser.set_pattern(
            parser_pattern, parser_type, parser_name, parser_example, analytics)

        self.messages = temp_parser.as_list()
        self.messages.append(constants.SAVE_CURRENT_PATTERN)
        self.previous_render = None  # Force render
        self.render_text_in_output()
        self.activate_prompt()
        final_res = self.box.gather().strip()
        if final_res == ':q':
            return
        temp_parser.save()
        self.messages = []

    def config_mode(self) -> None:
        """
        Start the configuration setup
        """
        self.current_end = 0
        self.messages = constants.CONFIG_START_MESSAGES
        self.previous_render = None  # Force render
        self.render_text_in_output()
        choice = None
        while choice not in {'session', 'parser'}:
            self.activate_prompt()
            choice = self.box.gather().strip()
            if choice == ':q':
                self.stop()
                break
        if choice == 'session':
            self.handle_create_session()
        elif choice == 'parser':
            self.handle_create_parser()

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
                self.stop()
            elif ':poll' in command:
                try:
                    command = float(command.replace(':poll', ''))
                    self.poll_rate = command
                    for stream in self.streams:
                        stream.poll_rate = command
                except ValueError:
                    pass
            elif ':config' in command:
                self.config_mode()
        self.reset_command_line()

    def start(self) -> None:
        """
        Starts the program
        """
        curses.wrapper(self.main)

    def stop(self) -> None:
        """
        Die if we send an exit signal of -1
        """
        for stream in self.streams:
            stream.exit()
        self.exit_val = -1

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
                    self.handle_command_mode()
                elif keypress == 'h':
                    self.previous_render = None  # Force render
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
                    self.previous_render = None  # Force render
                    # Swap stdout and stderr
                    self.reset_parser()
                    self.reset_regex_status()
                    if self.messages is self.stderr_messages:
                        self.messages = self.stdout_messages
                    else:
                        self.messages = self.stderr_messages
                elif keypress == 'p':
                    # Enable parser
                    if self.parser is not None:
                        self.reset_parser()
                    self.setup_parser()
                elif keypress == 'a':
                    # Enable analytics engine
                    if self.parser is not None:
                        self.last_index_processed = 0
                        self.parser.reset_analytics()
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
                    self.previous_render = None  # Force render
                elif keypress == 'KEY_DOWN':
                    # Scroll down
                    self.manually_controlled_line = True
                    self.stick_to_top = False
                    self.stick_to_bottom = False
                    if self.matched_rows:
                        self.current_end = min(
                            len(self.matched_rows) - 1, self.current_end + 1)
                    else:
                        self.current_end = min(
                            len(self.messages) - 1, self.current_end + 1)
                    self.previous_render = None  # Force render
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
                if self.exit_val == -1:
                    return
                if self.parser:
                    self.process_parser()  # This may block if there are a lot of messages
                if self.func_handle:
                    self.process_matches()  # This may block if there are a lot of messages
                self.render_text_in_output()
