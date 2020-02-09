# Logria Documentation

This folder contains the documentation on how to interact with Logria programmatically as well as how to leverage its feature-set as a user.

## Index

- [Patterns](patterns.md)
  - Details on how to configure patterns for log parsing
- [Sessions](sessions.md)
  - Details on how to configure sessions when launching the app

## Profiling

Profiling a 30 second sample with `python -m cProfile -s time logria/__main__.py` with two streams yields the following data:

```zsh
  21320022 function calls (21319138 primitive calls) in 30.534 seconds

  Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   479871    4.315    0.000   11.239    0.000 color_handler.py:82(_add_line)
  2641427    3.311    0.000    3.311    0.000 {method 'addstr' of '_curses.window' objects}
    58944    1.694    0.000    1.694    0.000 {method 'poll' of 'select.poll' objects}
    97377    1.544    0.000    1.544    0.000 {method 'refresh' of '_curses.window' objects}
  1919472    1.204    0.000    2.078    0.000 color_handler.py:70(_color_str_to_color_pair)
  2399343    1.074    0.000    1.074    0.000 color_handler.py:59(_get_color)
  2639294    0.966    0.000    0.966    0.000 {method 'split' of 'str' objects}
   239938    0.612    0.000   12.095    0.000 color_handler.py:106(_inner_addstr)
  5073679    0.606    0.000    0.606    0.000 {built-in method builtins.len}
    58944    0.466    0.000    3.532    0.000 connection.py:916(wait)
  2399343    0.443    0.000    0.443    0.000 {built-in method _curses.color_pair}
    12104    0.372    0.000   14.734    0.001 shell_output.py:257(render_text_in_output)
   239938    0.340    0.000   12.528    0.000 color_handler.py:121(addstr)
        1    0.288    0.288   30.492   30.492 shell_output.py:452(main)
    58944    0.208    0.000    0.512    0.000 selectors.py:234(register)
    85273    0.205    0.000    0.321    0.000 textpad.py:95(do_command)
```
