"""
Main app loop
"""

import sys
import os
import argparse

from logria.communication.input_handler import CommandInputStream, PipeInputStream
from logria.communication.shell_output import Logria


def main():
    """
    Main app loop, handles parsing args and starting the app
    """
    if not os.isatty(0):
        # If we are getting piped to, use that input stream only
        raise ValueError('Piping is not supported!')
    else:
        # Args if we are passed -h
        parser = argparse.ArgumentParser(
            description='A powerful CLI tool that puts log analytics at your fingertips.'
        )
        parser.add_argument('-e', action='append', type=str,
                            help='Command to pass through that will stream into this program, ex: logria -e \'tail -f log.txt\'')

        args = parser.parse_args()
        if args.e:
            args = args.e[0].split(' ')
            # args = args.e
        else:
            args = ['python', 'logria/communication/generate_test_logs.py']
        stream = CommandInputStream(args)

    # Start the app
    app = Logria(stream)
    app.start()
    stream.exit()


if __name__ == '__main__':
    main()
