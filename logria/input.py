import sys
from subprocess import Popen, PIPE
import os

def get_input_stream(args):
    """
    Given a command passed as an array ['python', 'script.py'], open a pipe to it and read the 
    """
    if not args:
        raise ValueError('No args!')
    with Popen(args, stdout=PIPE, bufsize=1,
            universal_newlines=True) as p:
        for line in p.stdout:
            print(line)


def get_input_file(filepath):
    with open(filepath, 'r') as f:
        for line in f.readlines():
            print(line)


if __name__ == '__main__':
    # get_input_file('README.MD')
    args = sys.argv[1:]
    get_input_stream(args)
