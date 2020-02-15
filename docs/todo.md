# Todo

- Enhancements
  - [ ] Support line breaks - requires rework of rendering logic
  - [ ] Make the command line show what current command is active, ex `/` for regex mode, `:` for command, etc
  - [ ] Spawn a subprocess to find all the matches in the list of messages
  - [ ] New "event loop" to handle multiple feature-sets, i.e. other than just regex search
- New features
  - [ ] Add 'status bar' since we have an empty row so the user can see what we are currently doing
- Clerical
  - [ ] Write docs
  - [ ] Add contribution guidelines

## Todos with Caveats

- [ ] Support optional piping as input stream - [SO Link](https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin)
  - Not possible to implement
  - stdin gets taken over by whatever we pipe to this program, and we cannot move that pipe away from stdin until the pipe finishes
  - We can overwrite the pipe with `sys.stdin = open(0)` however this will not work until the original pipe ends, which will never happen when tailing a stream
- [x] Highlight match in log - requires rework of regex method
  - We cannot just add ANSI codes as we might overwrite/alter existing ones
  - We also cannot just use a reset code after we insert a new code because it may reset what was already in the message
  - Current workaround is to regex out all color codes before inserting a highlighter and toggle

## Completed

- [x] Screenshots for readme
- [x] Add license
- [x] Add statistics tracking for log messages
- [x] Allow user to define multiple streams e.x. `ssh` sessions, and have a class to join them together
- [x] Main app loop starts when we call start, but the listener happens on init
- [x] Save sessions through class, make init process nicer
- [x] Init screen when launched with no args
- [x] Class for parsing paths for shell commands, i.e. resolving paths to tools on the `PATH`
- [x] Support parsing logs using `Log()` class
- [x] Switch between stderr and stdout
- [x] Move `regex_test_generator` to a separate class/module
- [x] Toggle insert mode (default off)
- [x] Add app entry method to `setup.py`
- [x] Regex searches through pre-formatted string, not color formatted string - requires rework of regex method
- [x] Make window scroll
- [x] Move with arrow keys
- [x] Refactor to class
- [x] Handle editor validation
- [x] Make backspace work

## Rejected

- [ ] Multiprocessing manager dict for `{stdout: [], stdin: []}`
  - This is not possible because to access the data in the array we must wait for the subprocess to complete, which defeats the purpose of this app. See branch `test/cs/multiprocessing-dict` for more info.