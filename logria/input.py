"""
Functions for handling getting input from a file or from stdout/stderr
"""


import sys
from subprocess import Popen, PIPE


def get_input_stream(args: list, processing_func=None) -> None:
    """
    Given a command passed as an array ['python', 'script.py'], open a
    pipe to it and read the contents
    """
    if not args:
        raise ValueError('No args!')
    with Popen(args, stdout=PIPE, bufsize=1,
               universal_newlines=True) as p_in:
        for line in p_in.stdout:
                        if processing_func:
                processing_func(line)
            else:
                print(line)


def get_input_file(filepath: str, processing_func=None) -> None:
    """
    Given a filename, open the file and read the contents
    """
    with open(filepath, 'r') as f_in:
        for line in f_in.readlines():
            if processing_func:
                processing_func(line)
            else:
                print(line)


if __name__ == '__main__':
    # get_input_file('README.MD')
    ARGS = sys.argv[1:]
    get_input_stream(ARGS)
