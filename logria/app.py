"""
Main app loop
"""

from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria

if __name__ == '__main__':
    args = ['python', 'logria/communication/generate_test_logs.py']
    stream = CommandInputStream(args)

    app = Logria(stream.stderr)
    app.start()

    stream.exit()
