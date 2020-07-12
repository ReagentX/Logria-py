"""
Main app loop
"""

import argparse
import os

from logria import APP_NAME, VERSION
from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria


def main():
    """
    Main app loop, handles parsing args and starting the app
    """
    # pylint: disable=no-else-raise
    if not os.isatty(0):
        # If we are getting piped to, use that input stream only
        raise ValueError('Piping is not supported!')
    else:
        # Args if we are passed -h
        parser = argparse.ArgumentParser(
            description='A powerful CLI tool that puts log analytics at your fingertips.'
        )
        parser.add_argument('-v', '--version', action='version',
                            version=f'{APP_NAME} {VERSION}')
        parser.add_argument('-e', action='append', type=str,
                            help='Command to pass through that will stream into this program, ex: logria -e \'tail -f log.txt\'')
        parser.add_argument('--no-cache', dest='no_cache', default=False, action='store_true',
                            help='Disable command history disk cache')

        args = parser.parse_args()
        if args.e:
            args = args.e[0].split(' ')
            stream = CommandInputStream(args)
            stream.start()
        else:
            stream = None

    # Start the app
    # If the stream is None, the app will ask the user to init
    app = Logria(stream, args.no_cache)
    app.start()


if __name__ == '__main__':
    main()
