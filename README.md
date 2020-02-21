![Logria Logo](/resources/branding/logria.svg)

# Logria

A powerful CLI tool that puts log analytics at your fingertips.

## tl;dr

- Live filtering of stream or streams from other executed processes, replacing `grep`
- Replace regex/filter without killing the process or losing the stream's history
- Parse logs using user-defined rules, apply analytics methods on top
- No dependencies

## Installation

There are several options to install this app.

### Normal Usage

`pip install logria`

### Development

#### Installing as a standalone app

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

#### Installing as part of another app

- `clone` the repository to your `venv` folder
  - Be sure your virtual environment is active
- Install Logria
  - `python setup.py install`

## Usage

There are a few main ways to invoke Logria:

- Directly:
  - `logria`
- With args:
  - `logria -e 'tail -f log.txt'`
- ~~As a pipe:~~
  - ~~`tail -f log.txt | logria`~~ [See Todos with Caveats](#todos-with-caveats)

It may also be imported and invoked programmatically as part of other software:

```python
from logria.communication.input_handler import CommandInputStream
from logria.communication.shell_output import Logria


process_to_read = ['python', 'sample_streams/generate_test_logs.py']
stream = CommandInputStream(process_to_read)
app = Logria(stream)  # Capture output from `process_to_read`
app.start()
```

## Key Commands

| Key | Command |
|--|--|
| `:` | [command mode](docs/commands.md) |
| `/` | regex search |
| `h` | if regex active, toggle highlighting of matches |
| `i` | toggle insert mode (default off) |
| `p` | activate parser |
| `a` | toggle analytics mode when parser is active |
| `z` | deactivate parser |
| ↑ | scroll buffer up one line |
| ↓ | scroll buffer down one line |
| → | skip and stick to end of buffer |
| ← | skip and stick to beginning of buffer |

## Features

Here are some of ways you can leverage Logria

### Live stream of log data

![logria](/resources/screenshots/logria.png)

### Interactive, live, editable grep

![regex](/resources/screenshots/regex.png)

### Live log message parsing

![parser](/resources/screenshots/parser.png)

### Live analytics/statistics tracking

![analytics](/resources/screenshots/analytics.png)

### User-defined saved sessions

See [session](/docs/sessions.md) docs.

### User-defined saved log parsing methods

See [patterns](/docs/patterns.md) docs.
