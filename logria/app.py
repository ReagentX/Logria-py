"""
Main app loop
"""

from logria.analytics import summarize_logs
from logria.support import input_handler

if __name__ == '__main__':
    log_handler = summarize_logs.ParseStandardLog()
    args = ['python', 'logria/support/generate_test_logs.py']
    input_handler.get_input_stream(args,
                                   processing_func=log_handler.handle)
