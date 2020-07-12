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

This is the rate at which we check the queues for new messages as well as check for user input. The poll rate defaults to 0.001. Values larger than 0.1 will make the app feel slow, as we will not render keystrokes while waiting.
