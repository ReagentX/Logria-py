"""
Main app loop
"""

import argparse

from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria


def main():
    """
    Main app loop, handles parsing args and starting the app
    """
    parser = argparse.ArgumentParser(
        description='A powerful CLI tool that puts log analytics at your fingertips.'
    )
    parser.add_argument('-e', action='append', type=str,
                        help='Command to pass through that will stream into this program, ex: logria -e \'tail -f log.txt\'')

    args = parser.parse_args()
    print(args)
    if args.e:
        args = args.e[0].split(' ')
        # args = args.e
    else:
        args = ['python', 'logria/communication/generate_test_logs.py']
    stream = CommandInputStream(args)

    app = Logria(stream.stderr)
    app.start()

    stream.exit()


if __name__ == '__main__':
    main()
