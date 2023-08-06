# Compare package versions in all their varied glory.

## Description

This module provides the `compare()` function which compares two
version strings and returns a negative value, zero, or a positive
value depending on whether the first string represents a version
number lower than, equal to, or higher than the second one, and
the `key_compare()` function which may be used as a key for e.g.
`sorted()`.

This module does not strive for completeness in the formats of
version strings that it supports. Some version strings sorted by
its rules are:

- 0.1.0
- 0.2.alpha
- 0.2
- 0.2.1
- 0.2a
- 0.2a.1
- 0.2a3
- 0.2a4
- 0.2p3
- 1.0~bpo3
- 1.0.beta
- 1.0.beta.2
- 1.0.beta2
- 1.0.beta3
- 1.0
- 1.0.4
- 1:0.3

## Contact

This module is [developed in a Gitlab repository][gitlab].
The author is [Peter Pentchev][roam].

## Version history

### 2.2.2 (2022-06-26)

- drop Python 3.6 support
- drop the no-self-use ignore and make sure pylint is 2.14+ so that
  it does not produce that warning by default
- add an EditorConfig definitions file
- reformat the source code using 100 characters per line
- use type | None instead of Optional[type]
- use single-dispatch functions for the command-line tool's subcommands
- add a `test_cargo` tool that fetches the version information about
  some crates from Cargo's crates.io index and then uses the command-line
  `trivver` tool to sort the version strings

### 2.2.1 (2022-04-27)

- bugfix: stop `version_compare_split()` from modifying its arguments!
- use black version 22 for source code formatting
- work around Pylint not recognizing a Callable value as, well, callable
- drop the obsolete "basepython = python3" lines from the Tox configuration

### 2.2.0 (2021-11-12)

- if the version string contains a `:` character, it is treated as
  a separator between a single number representing an epoch and
  the rest of the version identifier. Version strings containing more
  than one `:` character or ones where the portion before the `:`
  character is not a valid number are considered invalid and
  the comparison functions will raise an `InvalidEpochError`

### 2.1.0 (2021-10-24)

- expose the `version_compare_split()` function; it may be useful in
  other Python projects, too
- add Python 3.9 to the list of supported versions
- add a flake8 + hacking tox environment with some minor formatting
  fixes
- use unittest.mock instead of the standalone mock library

### 2.0.0 (2021-09-17)

- INCOMPATIBLE CHANGE: teach the comparison algorithm about strings
  followed by numbers, e.g. RedHat's .el7 suffixes, and also about
  Debian's ~bpo suffixes that should compare less than anything, even
  the empty string, similarly to .beta-style suffixes
- catch up with mypy's unbundling of type definitions for third-party
  libraries
- use black version 21 with no changes to the source code
- follow pylint's suggestion to use an f-string

### 1.0.1 (2021-03-30)

- add a MANIFEST.in file so that more files will be included in
  the source distribution even if built without `setuptools_scm`
- move some options to the tools invoked by tox.ini to the setup.cfg
  and pyproject.toml files

### 1.0.0 (2021-03-22)

- reformat the source code using black 20
- drop Python 2.x compatibility:
  - use types and modules from the Python 3 standard library
  - use type annotations, not type hints
  - subclass NamedTuple, using Python 3.6 variable type annotations
- switch to a declarative setup.cfg file
- install the module into the `unit_tests` tox environment
- add a PEP 517 buildsystem definition to the pyproject.toml file
- add the py.typed marker
- push the source down into a src/ subdirectory
- add a command-line utility exposing some of the functionality
- add a shell tool for testing the command-line utility
- add a manual page generated from an scdoc source file

### 0.1.0 (2020-03-22)

- first public release

[gitlab]: https://gitlab.com/ppentchev/python-trivver
[git]: https://gitlab.com/ppentchev/python-trivver.git
[roam]: mailto:roam@ringlet.net
