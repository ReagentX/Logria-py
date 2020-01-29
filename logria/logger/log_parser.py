"""
Placeholder log parser
"""

from datetime import datetime


class Log():
    """
    Class used to parse log statements written by the default logger to a usable form
    """

    def __init__(self, logstring: str):
        self.logstring = logstring
        self.log = logstring.split(' \x1b[0m- ')
        if len(self.log) != 5:
            self.is_valid_log = False
        else:
            self.is_valid_log = True
            self.time = datetime.strptime(self.log[0].replace(
                '\x1b[33m', ''), '%Y-%m-%d %H:%M:%S,%f')
            self.caller = self.log[1].replace('\x1b[34m', '')
            self.type = self.log[2].replace('\x1b[36m', '')
            self.process = self.log[3].replace('\x1b[32m', '')
            self.message = self.log[4]

    def as_dict(self):
        """
        Returns the log line as a dictionary
        """
        if self.is_valid_log:
            return {'time': self.time,
                    'caller': self.caller,
                    'type': self.type,
                    'process': self.process,
                    'message': self.message}
        return {'message': self.logstring}

    def __repr__(self):
        return str(self.as_dict())
