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
    """
    Spawns a process that will create queues we can read from to get input from a stream
    """

    def __init__(self, args: list) -> None:
        # Use separate queues for stdout/stderr so we can parse separately
        self.stdout = multiprocessing.Queue()
        self.stderr = multiprocessing.Queue()

        # Create the child process, have it run in the background
        self.process = multiprocessing.Process(
            target=self.run, args=(args, self.stdout, self.stderr,))
        self.process.daemon = True
        self.process.name = ' '.join(args)
        self.process.start()

    def run(self, args: list, stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Called by the process; should put data in stdoutq and/or stderrq
        """
        raise NotImplementedError('Input stream class initialized from parent!')


class CommandInputStream(InputStream):
    """
    Read a subprocess command as an input stream
    """

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
        LOGGER.info('Subprocess completed!')


class FileInputStream(InputStream):
    """
    Read in a file as a stream
    """

    def run(self, args: list, outputq: multiprocessing.Queue, _: multiprocessing.Queue) -> None:
        """
        Given a filename, open the file and read the contents
        args: a list of folders to be joined ['Docs', 'file.py'] -> 'Docs/file.py'
        """
        with open('/'.join(args), 'r') as f_in:
            for line in f_in.readlines():
                outputq.put(line)

def handle_stream(args):
    stream = CommandInputStream(args)
    while 1:
        if not stream.stdout.empty():
            out_log = stream.stdout.get()
            print('stdout:', out_log, end='', flush=True)
        if not stream.stderr.empty():
            err_log = stream.stderr.get()
            print('stderr:', err_log, end='', flush=True)

if __name__ == '__main__':
    # get_input_file('README.MD')
    ARGS = ['python', 'logria/communication/generate_test_logs.py']


    proc = multiprocessing.Process(target=handle_stream, args=(ARGS,))
    proc.name = 'StreamHandler'
    proc.start()
    var = ''
    while var != 'q':
        sys.stdout.flush()
        var = input('> ')
        sys.stdout.flush()
        print(var)
    proc.join()
