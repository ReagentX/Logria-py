"""
Main app loop
"""

from logria.analytics import summarize_logs
from logria.communication import input_handler
from logria.interface.build_app import build_app


APP = build_app()

def run():
    """
    Run the interface. (This runs the event loop until Ctrl-Q is pressed.)
    """
    APP.run()


if __name__ == '__main__':
    log_handler = summarize_logs.ParseStandardLog()
    args = ['python', 'logria/support/generate_test_logs.py']
    stream = input_handler.CommandInputStream(args)
    run()
