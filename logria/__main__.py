"""
Main app loop, receive CLI args
"""


import argparse
import os
import sys

from logria import APP_NAME, VERSION
from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria
from logria.utilities import constants

def main():
    """
    Main app loop, handles parsing args and starting the app
    """
    # Setup CLI args
    parser = argparse.ArgumentParser(
        description=constants.APP_DESCRIPTION,
    )
    parser.add_argument('-v', '--version', action='version',
                        version=f'{APP_NAME} {VERSION}')
    parser.add_argument('-e', action='append', type=str,
                        help=constants.EXEC_HELP)
    parser.add_argument('-c', '--no-cache', dest='no_cache', default=True, action='store_false',
                        help=constants.HISTORY_HELP)
    parser.add_argument('-n', '--no-smart-speed', dest='no_smart_speed', default=True, action='store_false',
                        help=constants.SMART_SPEED_HELP)

    args = parser.parse_args()

    # pylint: disable=no-else-raise
    if not os.isatty(0):
        # If we are getting piped to, use that input stream only
        print(constants.PIPE_INPUT_ERROR)
        sys.exit(-1)
    else:
        if args.e:
            command = args.e[0].split(' ')
            stream = CommandInputStream(command)
            stream.start()
        else:
            # If the stream is None, the app will ask the user to init
            stream = None
        app = Logria(stream, history_tape_cache=args.no_cache, smart_poll_rate=args.no_smart_speed)

    app.start()


if __name__ == '__main__':
    main()
