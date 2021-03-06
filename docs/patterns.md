# Patterns Documentation

A pattern is a regex patter with associated meta that Logria uses to parse log messages.

## Storage

Patterns are stored as `JSON` in `~/.logria/patterns` and do not have file extensions. A pattern is defined like so:

```json
{
    "pattern": " - ",
    "type": "split",
    "name": "Hyphen Separated",
    "example": "2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message",
    "analytics": {
      "Date": "date",
      "Caller": "count",
      "Level": "count",
      "Message": "sum"
    }
}
```

If `~/patterns` does not exist, Logria will create it.

## Types of Patterns

There are two types of patterns: `regex` and `split`. Both use regex, but in different ways. All patterns have four keys:

- `pattern`
  - The regex to use
- `type`
  - The method we intend to use the pattern, one of {`regex`, `split`}, detailed below
- `name`
  - The name of the pattern
- `example`
  - An example message to match with the pattern for UI/UX purposes
- `analytics`
  - A map of the name of the parsed message to a method to handle analytics
  - These are mapped internally by index, i.e. the first item in the dict maps to the first match
  - Methods currently include `count`, `sum`, and `average`, other methods are ignored

### Regex Patterns

A `regex` pattern matches parts of a log to the matches in a regex expression and looks like this:

```json
{
    "pattern": "([^ ]*) ([^ ]*) ([^ ]*) \\[([^]]*)\\] \"([^\"]*)\" ([^ ]*) ([^ ]*)",
    "type": "regex",
    "name": "Common Log Format",
    "example": "127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326",
    "analytics": {
        "Remote Host": "count",
        "User ID": "count",
        "Username": "count",
        "Date": "count",
        "Request": "count",
        "Status": "count",
        "Size": "count"
    }
}
```

### Split Patterns

A split pattern uses regex to split a message on a delimiter:

```json
{
    "pattern": " - ",
    "type": "split",
    "name": "Hyphen Separated",
    "example": "2005-03-19 15:10:26,773 - simple_example - CRITICAL - critical message",
    "analytics": {
        "Date": "date",
        "Caller": "count",
        "Level": "count",
        "Message": "sum"
    }
}
```

## Interpreting Patterns at Runtime

When activated, Logria will list the patterns defined in the patterns folder for the user to select based on the index of the filename:

```zsh
  0: Common Log Format
  1: Hyphen Separated
  2: Color + Hyphen Separated
```

Once a selection has been made, the user will be able to select which part of the matched log we will use when streaming:

```zsh
  0: 2020-02-04 19:06:52,852
  1: __main__.<module>
  2: MainProcess
  3: INFO
  4: I am a log! 91
```

This text is generated by the `example` key in the pattern's `json`.
