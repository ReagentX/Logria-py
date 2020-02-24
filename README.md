![Logria Logo](/resources/branding/logria.svg)

# Logria

A powerful CLI tool that puts log analytics at your fingertips.

## tl;dr

- Live filtering of data from other executed processes, replacing `grep`
- Use shell commands or files as input, save sessions and come back to them later
- Replace regex/filter without killing the process or losing the stream's history
- Parse logs using user-defined rules, apply analytics methods on top
- Pure Python, fully type hinted, zero dependencies

## Installation

There are several options to install this app.

### Normal Usage

`pip install logria`

### Development

See [Advanced Installation](docs/README.md#advanced-installation).

## Usage

There are a few main ways to invoke Logria:

- Directly:
  - `logria`
  - Opens to the setup screen
- With args:
  - `logria -e 'tail -f log.txt'`
  - Opens a pipe to 'tail -f log.txt'` and skips setup

For more details, see [Sample Usage Session](docs/README.md#sample-usage-session).

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
