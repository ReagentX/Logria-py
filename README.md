# Logria
 A powerful CLI tool that puts log analytics at your fingertips

![Logria Logo](/branding/logria.png)

## Notes

- Cannot use python-prompt-toolkit as it does not really support multiple input streams/sharing state between Application objects

## Todo

[ ] Regex searches through pre-formatted string, not color formatted string - requires rework of regex method
[ ] Highlight match in log - requires rework of regex method
[ ] Support optional piping - https://stackoverflow.com/questions/1450393/how-do-you-read-from-stdin
[ ] Main app loop starts when we call start, but the listener happens on init
[x] Make window scroll
[x] Move with arrow keys
[x] Refactor to class
[x] Handle editor validation
[x] Make backspace work
