"""
Main app loop
"""

import curses
import re
from curses.textpad import Textbox, rectangle


from logria.communication import input_handler
from logria.interface import color_handler


def get_input():
    return input('> ')


def render_text_in_window(window, last_row, lst, func=None):
    # clear the window
    for i in range(last_row):
        window.addstr(i, 2, '\n')
    current_row = 0
    for item in lst:
        # Subtract since we increment only if we write the row
        if current_row >= last_row - 2:
            break
        if func is None:
            current_row += 1
            # window.addstr(current_row, 2, item + '\n')
            color_handler.addstr(window, current_row, 2, item + '\n')
        elif func(item):
            current_row += 1
            # window.addstr(current_row, 2, item + '\n')
            color_handler.addstr(window, current_row, 2, item + '\n')
    window.refresh()


def regex_test_generator(pattern):
    return lambda string: bool(re.search(pattern, string))


def write_to_line(window, string, y=0, x=0):
    """
    Used for command line and status line
    """
    window.move(y, x)
    window.addstr(y, x, string)


def main(stdscr, q):
    stdscr.nodelay(True)
    stdscr.keypad(1)
    messages = []
    height, width = stdscr.getmaxyx()

    # Output window
    output_start_row = 0  # Leave space for top border
    output_height = height - 4  # Leave space for command line + status line
    last_row = output_height - output_start_row - 1
    outwin = curses.newwin(output_height, width - 1, output_start_row, 0)
    outwin.refresh()

    # Command line
    # lines, cols, start_height, start_left
    editwin = curses.newwin(1, width, height - 2, 1)
    editwin.nodelay(True)
    # upper left:  (height - 2, 0)
    # lower right: (height, width)
    rectangle(stdscr, height - 3, 0, height - 1, width - 2)
    stdscr.refresh()
    box = Textbox(editwin)

    # Handle for the processing func to check with when rendering output
    func_handle = None

    # Constant for the status line
    current_status = 'No filter'

    # Disable cursor:
    curses.curs_set(0)

    while True:

        # Update from the queue
        while not q.empty():
            message = q.get()
            messages.append(message)

        try:
            keypress = editwin.getkey()
            if keypress == ':':
                curses.curs_set(1)
                # Get resulting contents
                # write_to_command_line(editwin, height - 3, ':')
                box.edit()
                command = box.gather().strip()
                if command:
                    if command == ':q':
                        current_status = f'No filter'
                        func_handle = None
                        curses.curs_set(0)
                    else:
                        current_status = f'Regex with pattern /{command}/'
                        editwin.move(0, 0)
                        editwin.deleteln()
                        write_to_line(editwin, current_status)
                        func_handle = regex_test_generator(command)
                        render_text_in_window(
                            outwin, last_row, messages, func=regex_test_generator(command))
                        curses.curs_set(0)
            elif keypress == 'KEY_UP':
                pass
            elif keypress == 'KEY_DOWN':
                pass
            elif keypress == 'KEY_RIGHT':
                pass
            elif keypress == 'KEY_LEFT':
                pass
        except:
            render_text_in_window(outwin, last_row, messages, func=func_handle)



if __name__ == '__main__':
    args = ['python', 'logria/communication/generate_test_logs.py']
    stream = input_handler.CommandInputStream(args)

    curses.wrapper(main, stream.stderr)
    stream.exit()
