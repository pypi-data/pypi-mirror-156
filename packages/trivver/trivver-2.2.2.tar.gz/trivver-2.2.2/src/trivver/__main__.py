#
# Copyright (c) 2021, 2022  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
"""Command-line version comparison tool."""

from __future__ import annotations

import argparse
import dataclasses
import functools
import sys

from typing import Callable, Dict  # noqa: H301

from . import trivver


V_HANDLERS: Dict[str, Callable[[int], bool]] = {
    "<": lambda res: res < 0,
    "=": lambda res: res == 0,
    ">": lambda res: res > 0,
    "<=": lambda res: res <= 0,
    ">=": lambda res: res >= 0,
    "!=": lambda res: res != 0,
}
V_ALIASES = {
    "lt": "<",
    "eq": "=",
    "gt": ">",
    "le": "<=",
    "ge": ">=",
    "ne": "!=",
}
V_CHOICES = sorted(V_HANDLERS) + sorted(V_ALIASES)


@dataclasses.dataclass(frozen=True)
class Mode:
    """What did they tell us to do?"""


@dataclasses.dataclass(frozen=True)
class ModeCompare(Mode):
    """Compare two version strings."""

    left: str
    right: str


@dataclasses.dataclass(frozen=True)
class ModeSort(Mode):
    """Sort a list of versions from the standard input stream to the standard output one."""


@dataclasses.dataclass(frozen=True)
class ModeVerify(Mode):
    """Check whether a version comparison relation holds true."""

    left: str
    rel: str
    right: str


def parse_args() -> Mode:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(prog="trivver")

    subp = parser.add_subparsers(help="trivver subcommands")

    cmd_p = subp.add_parser("compare", help="compare the specified versions")
    cmd_p.add_argument("left", type=str, help="the first version string")
    cmd_p.add_argument("right", type=str, help="the second version string")
    cmd_p.set_defaults(mode_func=lambda args: ModeCompare(left=args.left, right=args.right))

    cmd_p = subp.add_parser("verify", help="verify that a relation holds true")
    cmd_p.add_argument("left", type=str, help="the first version string")
    cmd_p.add_argument("rel", type=str, choices=V_CHOICES, help="the relation to verify")
    cmd_p.add_argument("right", type=str, help="the second version string")
    cmd_p.set_defaults(
        mode_func=lambda args: ModeVerify(left=args.left, rel=args.rel, right=args.right)
    )

    cmd_p = subp.add_parser("sort", help="sort a list of versions from stdin to stdout")
    cmd_p.set_defaults(mode_func=lambda _args: ModeSort())

    args = parser.parse_args()

    mode_func: Callable[[argparse.Namespace], Mode] | None = getattr(args, "mode_func", None)
    if mode_func is None:
        sys.exit("No command specified")

    return mode_func(args)  # pylint: disable=not-callable


@functools.singledispatch
def run(mode: Mode) -> None:
    """Dispatch to the correct subcommand handler."""
    sys.exit(f"Internal error: unhandled operation mode {mode!r}")


@run.register
def cmd_compare(mode: ModeCompare) -> None:
    """Compare the two versions specified."""
    res = trivver.compare(mode.left, mode.right)
    if res < 0:
        print("<")
    elif res > 0:
        print(">")
    else:
        print("=")


@run.register
def cmd_verify(mode: ModeVerify) -> None:
    """Verify that a relation holds true for the specified versions."""

    rel = V_ALIASES.get(mode.rel, mode.rel)
    handler = V_HANDLERS.get(rel)
    if handler is None:
        sys.exit(f"Invalid relation '{mode.rel}' specified, must be one of {' '.join(V_CHOICES)}")

    res = trivver.compare(mode.left, mode.right)
    sys.exit(0 if handler(res) else 1)


@run.register
def cmd_sort(_mode: ModeSort) -> None:
    """Sort a list of versions supplied on the standard input stream."""
    lines = [line.strip() for line in sys.stdin.readlines()]
    print("\n".join(sorted(lines, key=trivver.key_compare)))


def main() -> None:
    """Parse the command-line arguments, perform the required actions."""
    run(parse_args())


if __name__ == "__main__":
    main()
