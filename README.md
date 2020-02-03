![Logria Logo](/branding/logria.png)

# Logria

A powerful CLI tool that puts log analytics at your fingertips.

## Features

- Live filtering of stream or streams from other executed processes, replacing `grep`
- Full regex support
- Low-overhead, no dependencies

## Installation

There are two options to install this app.

### Installing as a standalone app (`brew`, `apt-get`, etc coming soon!)

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

### Installing as part of another app (`pip` coming soon!)

- `clone` the repository to your `venv` folder
  - Be sure your virtual environment is active
- Install Logria
  - `python setup.py install`

## Usage

There are a few main ways to invoke Logria:

- Directly:
  - `logria`
- With args:
  - `logria -e tail -f log.txt`
- As a pipe:
  - `tail -f log.txt | logria`

It may also be imported invoked programmatically as part of other software:

```python
from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria


process_to_read = ['python', 'logria/communication/generate_test_logs.py']
stream = CommandInputStream(process_to_read)
app = Logria(stream.stderr)  # Capture output from `process_to_read`s `stderr`
app.start()
```

## Key Commands

| Key | Command |
|--|--|
| `:` | command mode |
| `/` | regex search |
| `h` | if regex active, toggle highlighting of matches |
| ↑ | scroll buffer up one line |
| ↓ | scroll buffer down one line |
| → | skip to end of buffer |
| ← | skip to beginning of buffer |

## Notes / Caveats

- Cannot use python-prompt-toolkit as it does not really support multiple input streams/sharing state between Application objects
- [`textbox.edit()`](https://docs.python.org/3/library/curses.html#curses.textpad.Textbox.edit) is blocking; we will need another solution if we want to not block output rendering

## Todo

- [ ] Support optional piping as input stream - [SO Link](https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin)
- [ ] Main app loop starts when we call start, but the listener happens on init
- [ ] Add statistics tracking for log messages
- [ ] Support parsing logs using `Log()` class
- [ ] Support line breaks - requires rework of rendering logic
- [ ] Class for parsing paths for shell commands, i.e. resolving paths to tools on the `PATH`
- [ ] New "event loop" to handle multiple featuresets, i.e. other than just regex search
- [ ] Make the command line show what current command is active, ex `/` for regex mode, `:` for command, etc

### Todos with Caveats

- [x] Highlight match in log - requires rework of regex method
  - We cannot just add ANSI codes as we might overwrite/alter existing ones
  - We also cannot just use a reset code after we insert a new code because it may reset what was already in the message
  - Current workaround is to disable all color codes before inserting a highlighter and toggle

### Completed

- [x] Add app entry method to `setup.py`
- [x] Regex searches through pre-formatted string, not color formatted string - requires rework of regex method
- [x] Make window scroll
- [x] Move with arrow keys
- [x] Refactor to class
- [x] Handle editor validation
- [x] Make backspace work
