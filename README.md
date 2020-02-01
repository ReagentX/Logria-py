# Logria
 A powerful CLI tool that puts log analytics at your fingertips

![Logria Logo](/branding/logria.png)

## Key Commands

| Key | Command |
|--|--|
| `:` | regex search |
| `h` | if regex active, toggle highlighting of matches |
| ↑ | scroll buffer up one line |
| ↓ | scroll buffer down one line |
| → | skip to end of buffer |
| ← | skip to beginning of buffer |

## Notes

- Cannot use python-prompt-toolkit as it does not really support multiple input streams/sharing state between Application objects

## Todo

- [ ] Support optional piping as input stream - https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin
- [ ] Main app loop starts when we call start, but the listener happens on init

### Todos with Caveats

- [x] Highlight match in log - requires rework of regex method
  - Complex, because we cannot use ANSI codes as we might overwrite/alter existing ones
  - We also cannot just use a reset code after we insert a new code because it may reset what we already have
  - Current workaround is to disable all color codes before inserting a highlighter and toggle

### Completed

- [x] Regex searches through pre-formatted string, not color formatted string - requires rework of regex method
- [x] Make window scroll
- [x] Move with arrow keys
- [x] Refactor to class
- [x] Handle editor validation
- [x] Make backspace work