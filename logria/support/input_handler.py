"""
Functions for handling getting input from a file or from stdout/stderr
"""


import sys
from subprocess import Popen, PIPE
import multiprocessing

from logria.logger.default_logger import setup_default_logger

# Setup default logger
LOGGER = setup_default_logger(__name__)


class InputStream():
    def __init__(self, args: list) -> None:
        self.stdout = multiprocessing.Queue()
        self.stderr = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=self.run, args=(args, self.stdout, self.stderr,))
        self.process.daemon = True
        self.process.name = ' '.join(args)
        self.process.start()

    def run(self):
        raise NotImplementedError('Input stream class initialized from parent')


class CommandInputStream(InputStream):
    def run(self, args: list, stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Given a command passed as an array ['python', 'script.py'], open a
        pipe to it and read the contents
        """
        proc = Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1,
                     universal_newlines=True)
        while True:
            # This will not read python print() calls because print does not flush stdout by default
            # this can be enabled with `print('', flush=True)`
            stdout_output = proc.stdout.readline()
            if stdout_output == '' and proc.poll() is not None:
                break
            if stdout_output:
                stdoutq.put(stdout_output)
            stderr_output = proc.stderr.readline()
            if stderr_output == '' and proc.poll() is not None:
                break
            if stderr_output:
                stderrq.put(stderr_output)


class FileInputStream(InputStream):
    def run(self, filepath: str, processing_func=None) -> None:
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
    ARGS = ['python', 'logria/support/generate_test_logs.py']
    stream = CommandInputStream(ARGS)
    while 1:
        if not stream.stdout.empty():
            log = stream.stdout.get()
            print('stdout:', log, end='')
        if not stream.stderr.empty():
            log = stream.stderr.get()
            print('stderr:', log, end='')
