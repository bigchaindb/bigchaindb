# Python Style Guide

This guide starts out with our general Python coding style guidelines and ends with a section on how we write & run (Python) tests.

## General Python Coding Style Guidelines

Our starting point is [PEP8](https://www.python.org/dev/peps/pep-0008/), the standard "Style Guide for Python Code." Many Python IDEs will check your code against PEP8. (Note that PEP8 isn't frozen; it actually changes over time, but slowly.)

BigchainDB uses Python 3.4+, so you can ignore all PEP8 guidelines specific to Python 2.

### Python Docstrings

PEP8 says some things about docstrings, but not what to put in them or how to structure them. [PEP257](https://www.python.org/dev/peps/pep-0257/) was one proposal for docstring conventions, but we prefer [Google-style docstrings](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments) instead: they're easier to read and the [napoleon extension](http://www.sphinx-doc.org/en/stable/ext/napoleon.html) for Sphinx lets us turn them into nice-looking documentation. Here are some references on Google-style docstrings:

* [Google's docs on Google-style docstrings](https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments)
* [napoleon's docs include an overview of Google-style docstrings](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/index.html)
* [Example Google-style docstrings](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html) (from napoleon's docs)

### Maximum Line Length

PEP8 has some [maximum line length guidelines](https://www.python.org/dev/peps/pep-0008/#id17), starting with "Limit all lines to a maximum of 79 characters" but "for flowing long blocks of text with fewer structural restrictions (docstrings or comments), the line length should be limited to 72 characters."

We discussed this at length, and it seems that the consensus is: _try_ to keep line lengths less than 79/72 characters, unless you have a special situation where longer lines would improve readability. (The basic reason is that 79/72 works for everyone, and BigchainDB is an open source project.) As a hard limit, keep all lines less than 119 characters (which is the width of GitHub code review).

### Single or Double Quotes?

Python lets you use single or double quotes. PEP8 says you can use either, as long as you're consistent. We try to stick to using single quotes, except in cases where using double quotes is more readable. For example:
```python
print('This doesn\'t look so nice.')
print("Doesn't this look nicer?")
```

### Breaking Strings Across Multiple Lines

Should we use parentheses or slashes (`\`) to break strings across multiple lines, i.e.
```python
my_string = ('This is a very long string, so long that it will not fit into just one line '
             'so it must be split across multiple lines.')
# or
my_string = 'This is a very long string, so long that it will not fit into just one line ' \
            'so it must be split across multiple lines.'
```

It seems the preference is for slashes, but using parentheses is okay too. (There are good arguments either way. Arguing about it seems like a waste of time.)

### How to Format Long import Statements

If you need to `import` lots of names from a module or package, and they won't all fit in one line (without making the line too long), then use parentheses to spread the names across multiple lines, like so:
```python
from Tkinter import (Tk, Frame, Button, Entry, Canvas, Text,
    LEFT, DISABLED, NORMAL, RIDGE, END)
```

For the rationale, see [PEP 328](https://www.python.org/dev/peps/pep-0328/#rationale-for-parentheses).

### Using the % operator or `format()` to Format Strings

Given the choice:
```python
x = 'name: %s; score: %d' % (name, n)
# or
x = 'name: {}; score: {}'.format(name, n)
```

we use the `format()` version. The [official Python documentation says](https://docs.python.org/2/library/stdtypes.html#str.format), "This method of string formatting is the new standard in Python 3, and should be preferred to the % formatting described in String Formatting Operations in new code."


## Writing and Running (Python) Unit Tests

We write unit tests for our Python code using the [pytest](http://pytest.org/latest/) framework.

All tests go in the `bigchaindb/tests` directory or one of its subdirectories. You can use the tests already in there as templates or examples.

You can run all unit tests using:
```text
py.test -v
```

or, if that doesn't work, try:
```text
python -m pytest -v
```

or:
```text
python setup.py test
```

If you want to learn about all the things you can do with pytest, see [the pytest documentation](http://pytest.org/latest/).

**Automated testing of pull requests.** We use [Travis CI](https://travis-ci.com/), so that whenever someone creates a new BigchainDB pull request on GitHub, Travis CI gets the new code and does _a bunch of stuff_. You can find out what we tell Travis CI to do in [the `.travis.yml` file](.travis.yml): it tells Travis CI how to install BigchainDB, how to run all the tests, and what to do "after success" (e.g. run `codecov`). (We use [Codecov](https://codecov.io/) to get a rough estimate of our test coverage.)
