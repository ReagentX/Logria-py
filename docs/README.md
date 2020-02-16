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

## Profiling

Profiling a 40 second sample with `python -m cProfile -s time logria/__main__.py` with two streams yields the following data:

```zsh
  29748922 function calls (29748037 primitive calls) in 39.801 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    13094   11.214    0.001   11.214    0.001 {built-in method time.sleep}
   850733    4.772    0.000    4.772    0.000 {method 'refresh' of '_curses.window' objects}
   518922    4.524    0.000   11.441    0.000 color_handler.py:82(_add_line)
  2856478    3.290    0.000    3.290    0.000 {method 'addstr' of '_curses.window' objects}
   837638    2.049    0.000    3.268    0.000 textpad.py:95(do_command)
   837638    1.416    0.000    1.416    0.000 {method 'getch' of '_curses.window' objects}
    63124    1.240    0.000    1.240    0.000 {method 'poll' of 'select.poll' objects}
  2075672    1.233    0.000    2.018    0.000 color_handler.py:70(_color_str_to_color_pair)
  2594594    0.997    0.000    0.997    0.000 color_handler.py:59(_get_color)
  2854070    0.986    0.000    0.986    0.000 {method 'split' of 'str' objects}
  5495758    0.645    0.000    0.645    0.000 {built-in method builtins.len}
   259463    0.638    0.000   12.325    0.000 color_handler.py:106(_inner_addstr)
  2594594    0.468    0.000    0.468    0.000 {built-in method _curses.color_pair}
   837644    0.438    0.000    0.590    0.000 textpad.py:51(_update_max_yx)
    63124    0.436    0.000    3.013    0.000 connection.py:916(wait)
    13095    0.397    0.000   15.025    0.001 shell_output.py:286(render_text_in_output)
   259463    0.369    0.000   12.792    0.000 color_handler.py:121(addstr)
        1    0.296    0.296   39.713   39.713 shell_output.py:533(main)
   837638    0.278    0.000    0.514    0.000 ascii.py:62(isprint)
   838352    0.237    0.000    0.237    0.000 ascii.py:48(_ctoi)
    63124    0.206    0.000    0.503    0.000 selectors.py:234(register)
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
