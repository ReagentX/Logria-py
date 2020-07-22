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
        parser.add_argument('-c', '--no-cache', dest='no_cache', default=True, action='store_false',
                            help='Disable command history disk cache')
        parser.add_argument('-n', '--no-smart-speed', dest='no_smart_speed', default=True, action='store_false',
                            help='Disable variable speed polling based on message receive speed')

        args = parser.parse_args()
        if args.e:
            args = args.e[0].split(' ')
            stream = CommandInputStream(args)
            stream.start()
        else:
            stream = None

    # Start the app
    # If the stream is None, the app will ask the user to init
    app = Logria(stream, history_tape_cache=args.no_cache, smart_poll_rate=args.no_smart_speed)
    app.start()


if __name__ == '__main__':
    main()
