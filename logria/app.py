"""
Main app loop
"""

import curses
import re
from curses.textpad import Textbox, rectangle


from logria.communication import input_handler
from logria.interface import color_handler

stdscr = curses.initscr()


def get_input():
    return input('> ')


def render_text_in_window(window, last_row, lst, func=None):
    # clear the window
    for i in range(last_row):
        window.addstr(i, 2, '\n')
    current_row = 0
    for item in lst:
        # Subtract since we increment only if we write the row
        if current_row >= last_row - 1:
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


def main(stdscr, q):
    messages = []
    height, width = stdscr.getmaxyx()

    # Output window
    output_start_row = 0  # Leave space for top border
    output_height = height - 3  # Leave space for command line
    last_row = output_height - output_start_row - 1
    outwin = curses.newwin(output_height, width - 1, output_start_row, 0)
    outwin.border(0)
    outwin.refresh()

    # Command line
    # lines, cols, start_height, start_left
    editwin = curses.newwin(1, width, height - 2, 1)
    # upper left:  (height - 2, 0)
    # lower right: (height, width)
    rectangle(stdscr, height - 3, 0, height - 1, width - 2)
    stdscr.refresh()
    box = Textbox(editwin)

    while True:
        # This all needs to happen at the same time, maybe in an event loop?

        while not q.empty():
            message = q.get()
            messages.append(message)

        # Get resulting contents
        box.edit()
        command = box.gather().strip()
        if command:
            if command == ':q':
                break
            else:
                render_text_in_window(
                    outwin, last_row, messages, func=regex_test_generator(command))
        else:
            render_text_in_window(outwin, last_row, messages)
        # outwin.refresh()


if __name__ == '__main__':
    args = ['python', 'logria/communication/generate_test_logs.py']
    stream = input_handler.CommandInputStream(args)
    curses.wrapper(main, stream.stderr)
    stream.exit()
