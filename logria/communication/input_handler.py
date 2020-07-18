"""
Functions for handling getting input from a file or from stdout/stderr
"""


import time
import multiprocessing
from subprocess import PIPE, Popen
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK
from typing import List


class InputStream():
    """
    Spawns a process that will create queues we can read from to get input from a stream
    """

    def __init__(self, args: List[str], poll_rate=0.001) -> None:
        # Poll processes for new messages at this rate
        self.poll_rate = poll_rate

        # Use separate queues for stdout/stderr so we can parse separately
        self.stdout: multiprocessing.Queue = multiprocessing.Queue()
        self.stderr: multiprocessing.Queue = multiprocessing.Queue()

        # Create the child process, have it run in the background
        self.process = multiprocessing.Process(
            target=self.run, args=(args, self.stdout, self.stderr,))
        self.process.name = ' '.join(args)

    def start(self):
        """
        Start the process independent of init
        """
        self.process.start()

    def run(self, args: List[str], stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Called by the process; should put data in stdoutq and/or stderrq
        """
        raise NotImplementedError(
            'Input stream class initialized from parent!')

    def exit(self):
        """
        Kills the process
        """
        self.process.terminate()


class CommandInputStream(InputStream):
    """
    Read a subprocess command as an input stream
    """

    def __init__(self, args, poll_rate=0.001):
        super().__init__(args, poll_rate=poll_rate)
        self.proc = None

    def run(self, args: List[str], stdoutq: multiprocessing.Queue, stderrq: multiprocessing.Queue) -> None:
        """
        Given a command passed as an array ['python', 'script.py'], open a
        pipe to it and read the contents

        This will not read python print() calls because print does not flush stdout by default,
          this can be enabled with `print('', flush=True)`
        """
        try:
            self.proc = Popen(args, stdout=PIPE, stderr=PIPE, bufsize=1,
                              universal_newlines=True)

            # Un-buffer streams
            stdout_flag = fcntl(self.proc.stdout, F_GETFL)  # type: ignore
            fcntl(self.proc.stdout, F_SETFL, stdout_flag | O_NONBLOCK)  # type: ignore

            stderr_flag = fcntl(self.proc.stderr, F_GETFL)  # type: ignore
            fcntl(self.proc.stderr, F_SETFL, stderr_flag | O_NONBLOCK)  # type: ignore

            while True:
                time.sleep(self.poll_rate)
                # stdout
                stdout_output = self.proc.stdout.readline()  # type: ignore
                if stdout_output:
                    stdoutq.put(stdout_output)

                # stderr
                stderr_output = self.proc.stderr.readline()  # type: ignore
                if stderr_output:
                    stderrq.put(stderr_output)

                # Kill condition
                if stderr_output == '' and stdout_output == '' and self.proc.poll() is not None:
                    break
        except PermissionError:
            stderrq.put(
                f'Permissions error opening handle to command: {"/".join(args)}')
        except FileNotFoundError:
            stderrq.put(
                f'File not found error opening handle to command: {"/".join(args)}')

    def exit(self):
        """
        Kills the process
        """
        if self.proc is not None:
            # Proc may be dead already when we get here
            self.proc.kill()  # Kill piped process
            self.proc.communicate()  # Make sure any final data is not left in the pipe
        self.process.terminate()  # Kill Python process


class PipeInputStream(InputStream):
    """
    Read in a pipe as a stream
    """
    # pylint: disable=arguments-differ
    def run(self, pipe, stdoutq: multiprocessing.Queue, _: multiprocessing.Queue) -> None:
        """
        Given a filename, open the file and read the contents
        args: a list of folders to be joined ['Docs', 'file.py'] -> 'Docs/file.py'
        """
        # pipe = open(0)
        while True:
            time.sleep(self.poll_rate)
            try:
                pipe_input = pipe.readline()
                if pipe_input:
                    stdoutq.put(pipe_input)
            # pylint: disable=bare-except
            except:
                break


class FileInputStream(InputStream):
    """
    Read in a file as a stream
    """

    def run(self, args: List[str], stdoutq: multiprocessing.Queue, _: multiprocessing.Queue) -> None:
        """
        Given a filename, open the file and read the contents
        args: a list of folders to be joined ['Docs', 'file.py'] -> 'Docs/file.py'
        """
        try:
            with open('/'.join(args), 'r') as f_in:
                for line in f_in.readlines():
                    stdoutq.put(line)
        except PermissionError:
            _.put(
                f'Permissions error opening file handle to: {"/".join(args)}')
        except FileNotFoundError:
            stdoutq.put(
                f'File not found error opening handle to command: {"/".join(args)}')


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
