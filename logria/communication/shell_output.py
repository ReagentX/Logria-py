import curses
import time
import re
from curses.textpad import Textbox, rectangle
import multiprocessing

from logria.communication import input_handler, keystrokes
from logria.interface import color_handler


class Logria():
    def __init__(self, q):
        self.q = q  # Input queue
        self.messages = []  # Message buffer

        # Handle when we are filtering
        self.matched_rows = []  # Int array of matches when filtering is active
        self.last_index_searched = 0  # The last index the filtering function saw

        self.current_status = ''  # Current status, aka what is in the command line
        self.func_handle = None  # Regex func that handles filtering
        self.last_row = None  # The last row we can render, aka number of lines
        self.editing = False  # Whether we are currently editing the command
        self.stick_to_bottom = True  # Whether we should follow the stream
        self.stick_to_top = False  # Whether we should stick to the top and not render new lines
        self.manually_controlled_line = False  # Whether manual scroll is active
        self.current_end = 0  # Current last row we have rendered

    def clear_output_window(self):
        """
        Clears the text rendered in the output window
        """
        for i in range(self.last_row):
            self.outwin.addstr(i, 2, '\n')

    def render_text_in_output(self):
        """
        Renders stream content in the output window

        If filters are inactive, we use `messages`. If they are active, we pull from `matched_rows`
        """
        self.clear_output_window()
        current_row = 0  # The row we are currently rendering

        # If filters are disabled
        if self.func_handle is None:
            # Handle where the bottom of the stream should be
            if self.stick_to_bottom:
                end = len(self.messages)
            elif self.stick_to_top:
                end = min(self.last_row, len(self.messages))
            elif self.manually_controlled_line:
                if len(self.messages) < self.last_row:
                    # If have fewer messages than lines, just render it all
                    end = len(self.messages)
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
                if current_row >= self.last_row - 2:
                    break
                current_row += 1
                # Instead of window.addstr, handle colors
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
                # Instead of window.addstr, handle colors
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

        # For each message, add its index to the list of matches; this is more efficient than
        # Storing a second copy of each match
        for index in range(self.last_index_searched, len(self.messages)):
            if self.func_handle(self.messages[index]):
                self.matched_rows.append(index)
        self.last_index_searched = len(self.messages)

    def regex_test_generator(self, pattern):
        """
        Return a function that will test a string against `pattern`
        """
        return lambda string: bool(re.search(pattern, string))

    def write_to_command_line(self, string):
        """
        Writes a message to the command line
        """
        self.reset_command_line()
        curses.curs_set(1)
        self.command_line.move(0, 0)
        self.command_line.addstr(0, 0, string)
        curses.curs_set(0)

    def reset_command_line(self):
        """
        Resets the command line
        """
        self.command_line.move(0, 0)
        self.command_line.deleteln()
        curses.curs_set(0)

    def activate_prompt(self):
        """
        Activate the prompt so we can edit it
        """
        self.editing = True
        self.reset_command_line()
        curses.curs_set(1)
        self.box.edit(keystrokes.validator)

    def handle_regex_command(self, command):
        """
        Handle a regex command
        """
        self.reset_regex_status()
        self.func_handle = self.regex_test_generator(command)

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

    def reset_regex_status(self):
        """
        Reset current regex/filter status to no filter
        """
        self.current_status = 'No filter applied'  # CLI message, renderd after
        self.func_handle = None  # Disable filter
        self.matched_rows = []  # Clear out matched rows
        self.last_index_searched = 0  # Reset the last searched index
        self.current_end = 0  # We now do not know where to end
        self.stick_to_bottom = True  # Stay at the bottom for the next render
        self.write_to_command_line(self.current_status)  # Render status

    def start(self):
        """
        Starts the program
        """
        curses.wrapper(self.main)

    def main(self, stdscr):
        """
        Main program loop, handles user control and logical flow
        """
        stdscr.keypad(1)
        height, width = stdscr.getmaxyx()  # Get screen size

        # Setup Output window
        output_start_row = 0  # Leave space for top border
        output_height = height - 2  # Leave space for command line
        self.last_row = output_height - output_start_row - 1  # The last row we can write to
        # Create the window with these sizes
        self.outwin = curses.newwin(
            output_height, width - 1, output_start_row, 0)
        self.outwin.refresh()

        # Setup Command line
        # 1 line, screen width, start 2 from the bottom, 1 char from the side
        self.command_line = curses.newwin(1, width, height - 2, 1)
        self.command_line.nodelay(True)  # Do not block the event loop waiting for input
        # Draw rectangle around the command line
        # upper left:  (height - 2, 0), 2 chars up on left edge
        # lower right: (height, width), bottom right corner of screen
        rectangle(stdscr, height - 3, 0, height - 1, width - 2)
        stdscr.refresh()
        self.box = Textbox(self.command_line)  # Editable text box element

        # Update the command line status
        self.reset_regex_status()

        # Disable cursor:
        curses.curs_set(0)
        # self.stdscr = stdscr
        while True:
            # Update messages from the input stream's queue, track time
            t_0 = time.perf_counter()
            while not self.q.empty():
                message = self.q.get()
                self.messages.append(message)

            # Prevent this loop from taking up 100% of the CPU dedicated to the main thread by delaying loops
            t_1 = time.perf_counter() - t_0
            time.sleep(max(0, 0.001 - t_1))  # Don't delay if the queue processing took too long

            try:
                keypress = self.command_line.getkey()  # Get keypress
                if keypress == ':':
                    # Handle getting input from the command line for regex
                    self.activate_prompt()
                    command = self.box.gather().strip()
                    if command:
                        if command == ':q':
                            self.reset_regex_status()
                        else:
                            self.handle_regex_command(command)
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
            except:
                # If we have an active filter, process it, always render
                if self.func_handle:
                    self.process_matches()  # This may block if there are a lot of messages
                self.render_text_in_output()
