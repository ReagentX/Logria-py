"""
Functions for handling getting input from a file or from stdout/stderr
"""


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

    def start(self):
        """
        Start the process independent of init
        """
        self.process.start()

    def run(self, args: list, stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Called by the process; should put data in stdoutq and/or stderrq
        """
        raise NotImplementedError(
            'Input stream class initialized from parent!')

    def exit(self):
        """
        Kills the process
        """
        self.process.join()
        self.process.close()


class CommandInputStream(InputStream):
    """
    Read a subprocess command as an input stream
    """

    def run(self, args: list, stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Given a command passed as an array ['python', 'script.py'], open a
        pipe to it and read the contents

        This will not read python print() calls because print does not flush stdout by default,
          this can be enabled with `print('', flush=True)`
        """
        proc = Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1,
                     universal_newlines=True)
        while True:
            # stdout
            stdout_output = proc.stdout.readline()
            if stdout_output:
                stdoutq.put(stdout_output)

            # stderr
            stderr_output = proc.stderr.readline()
            if stderr_output:
                stderrq.put(stderr_output)

            # Kill condition
            if stderr_output == '' and stdout_output == '' and proc.poll() is not None:
                break


class PipeInputStream(InputStream):
    """
    Read in a file as a stream
    """

    def run(self, pipe: PIPE, stdoutq: multiprocessing.Queue, _: multiprocessing.Queue) -> None:
        """
        Given a filename, open the file and read the contents
        args: a list of folders to be joined ['Docs', 'file.py'] -> 'Docs/file.py'
        """
        # pipe = open(0)
        while True:
            try:
                pipe_input = pipe.readline()
                if pipe_input:
                    stdoutq.put(pipe_input)
            except:
                pass


class FileInputStream(InputStream):
    """
    Read in a file as a stream
    """

    def run(self, args: list, stdoutq: multiprocessing.Queue, _: multiprocessing.Queue) -> None:
        """
        Given a filename, open the file and read the contents
        args: a list of folders to be joined ['Docs', 'file.py'] -> 'Docs/file.py'
        """
        with open('/'.join(args), 'r') as f_in:
            for line in f_in.readlines():
                stdoutq.put(line)


if __name__ == '__main__':
    cmd = ['python', 'logria/communication/generate_test_logs.py']
    stream = CommandInputStream(cmd)
    while 1:
        if not stream.stdout.empty():
            out_log = stream.stdout.get()
            print('stdout:', out_log, end='', flush=True)
        if not stream.stderr.empty():
            err_log = stream.stderr.get()
            print('stderr:', err_log, end='', flush=True)
