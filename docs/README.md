# Logria Documentation

This folder contains the documentation on how to interact with Logria programmatically as well as how to leverage its feature-set as a user.

## Index

- [Patterns](patterns.md)
  - Details on how to configure patterns for log parsing
- [Sessions](sessions.md)
  - Details on how to configure sessions when launching the app
- [Input Handler](input_handler.md)
  - Details on how input handler classes open subprocesses
- [Commands](commands.md)
  - Details on commands available in the app
- [Todo](todo.md)
  - List of tasks for the repo

## Advanced Installation

`pip install logria` is the best way to install the app for normal use.

### Installing as a standalone app

- `clone` the repository
- `cd` to the repository
- (Optional) Create a virtual environment (3.6+)
  - `python -m venv venv`
  - `source venv/bin/activate`
- (Optional) install requirements
  - These are only for some development tools and are not needed to run the app
  - `pip install -r requirements.txt`
- Install self
  - `deactivate` if we want to install globally, otherwise leave your `venv` active
  - `python setup.py develop` or `python setup.py install` depending on whether you are actively developing this app

### Installing as part of another app

- `clone` the repository to your `venv` folder
  - Be sure your virtual environment is active
- Install Logria
  - `python setup.py install`

## Sample Usage Session

Start Logria by invoking it as a command line application:

```zsh
chris@ChristophersMBP ~ % logria
```

This will launch the app and show us the splash screen:

```log
Enter a new command to open and save a new stream,
or enter a number to choose a saved session from the list,
or enter `:config` to configure.
Enter `:q` to quit.

0: File - readme
1: File - Sample Access Log
2: Cmd - Generate Test Logs
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│_
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Entering `2` will load and open handles to the commands in `Cmd - Generate Test Logs`:

```log
2020-02-23 16:56:10,786 - __main__.<module> - MainProcess - INFO - I am the first log in the list
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a first log! 21
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a second log! 71
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a first log! 43
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a second log! 87
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│No filter applied
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Typing `/` and entering `100` will filter our stream down to only lines that match that pattern:

```log
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a first log! 43
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a second log! 87
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│Regex with pattern /100/
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Typing `/` and entering `:q` will reset the filter:

```log
2020-02-23 16:56:10,786 - __main__.<module> - MainProcess - INFO - I am the first log in the list
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a first log! 21
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a second log! 71
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a first log! 43
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a second log! 87
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│No filter applied
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Typing `/` and entering `:q` will reset the filter:

```log
2020-02-23 16:56:10,786 - __main__.<module> - MainProcess - INFO - I am the first log in the list
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a first log! 21
2020-02-23 16:56:10,997 - __main__.<module> - MainProcess - INFO - I am a second log! 71
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a first log! 43
2020-02-23 16:56:11,100 - __main__.<module> - MainProcess - INFO - I am a second log! 87
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│No filter applied
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Typing `:` and entering `:q` will exit the app.

## Advanced Usage

Logria may also be imported and invoked programmatically as part of other software:

```python
import os
from logria.communication.input_handler import PipeInputStream
from logria.communication.shell_output import Logria


stream = PipeInputStream(os.pipe())
app = Logria(stream)  # Capture output from `process_to_read`
app.start()
```

## Profiling

Profiling a 40 second sample with `python -m cProfile -s time logria/__main__.py` with two streams yields the following data:

```zsh
  29748922 function calls (29748037 primitive calls) in 39.801 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    24167   23.427    0.001   23.427    0.001 {built-in method time.sleep}
   591677    2.517    0.000    2.517    0.000 {method 'refresh' of '_curses.window' objects}
    97914    2.164    0.000    2.164    0.000 {method 'poll' of 'select.poll' objects}
   591237    1.392    0.000    2.199    0.000 textpad.py:95(do_command)
   591237    0.974    0.000    0.974    0.000 {method 'getch' of '_curses.window' objects}
    97914    0.635    0.000    4.681    0.000 connection.py:916(wait)
        2    0.592    0.296    6.303    3.151 textpad.py:177(edit)
        1    0.493    0.493   36.647   36.647 shell_output.py:751(main)
   591249    0.304    0.000    0.394    0.000 textpad.py:51(_update_max_yx)
    97914    0.299    0.000    0.720    0.000 selectors.py:234(register)
    24166    0.279    0.000    0.279    0.000 {method 'getkey' of '_curses.window' objects}
    97914    0.220    0.000    2.385    0.000 selectors.py:402(select)
    97914    0.212    0.000    0.980    0.000 selectors.py:351(register)
    97914    0.193    0.000    0.380    0.000 selectors.py:347(__init__)
   591237    0.178    0.000    0.336    0.000 ascii.py:62(isprint)
    97914    0.160    0.000    4.840    0.000 connection.py:423(_poll)
   592681    0.158    0.000    0.158    0.000 ascii.py:48(_ctoi)
    97914    0.149    0.000    5.052    0.000 connection.py:253(poll)
     8242    0.146    0.000    0.400    0.000 color_handler.py:82(_add_line)
    97914    0.136    0.000    0.266    0.000 selectors.py:21(_fileobj_to_fd)
    24165    0.135    0.000    0.885    0.000 shell_output.py:364(render_text_in_output)
    97914    0.123    0.000    0.156    0.000 selectors.py:209(__init__)
    97914    0.121    0.000    0.166    0.000 selectors.py:268(close)
    97914    0.101    0.000    5.152    0.000 queues.py:122(empty)
```

## Guidelines

- "Brand" colors
  - Letters: ![#e63462](https://placehold.it/15/e63462/000000?text=+)`#e63462`
  - Accent: ![#333745](https://placehold.it/15/333745/000000?text=+)`#333745`
- Contributing
  - No pull request shall be behind develop
  - First come, first served
  - If anything breaks, the pull request will be queued again when the issue is resolved
  - Pull request comments will be resolved by the person who created them

## Notes / Caveats

- Cannot use python-prompt-toolkit as it does not really support multiple input streams/sharing state between Application objects
- [`textbox.edit()`](https://docs.python.org/3/library/curses.html#curses.textpad.Textbox.edit) is blocking; we will need another solution if we want to not block output rendering
- Curses will crash when writing to the last line of a window, but it will write correctly, so we wrap some instances of this in a try/except to ensure we don't crash when writing valid values
