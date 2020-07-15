# Commands

| Key | Command |
|--|--|
| `:` | enter command mode |
| `:q` | exit the program |
| `:poll #` | update [poll rate](#poll-rate) to #, where # is a number |
| `:config` | enter configuration mode to create sessions or patterns |
| `:history` | view and search the history tape |
| `:history #` | view and search the history tape's last # (integer) items |
| `:history off` | go back to the main app from history mode |

## Notes

To use a command, simply enter text after the `:`. If the `:` is deleted, the  command will be ignored.

### Poll Rate

This is the rate at which we check the queues for new messages as well as check for user input. Values higher than 0.01 will make the app feel sluggish, as we will not respond to keystrokes while waiting.

The poll rate defaults to `smart` mode, where Logria will calculate a rate at which to poll the message queues based on the speed of incoming messages. To disable this feature, pass `-n` when starting Logria. If `smart` mode is disabled, the app falls back to the default value of 0`.0001`.
