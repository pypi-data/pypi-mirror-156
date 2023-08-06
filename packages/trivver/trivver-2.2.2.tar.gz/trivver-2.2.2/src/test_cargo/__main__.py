"""Run some tests using the crates.io index."""

import argparse
import functools
import json
import os
import pathlib
import posix
import pwd
import random
import re
import subprocess
import sys
import tempfile
import time

from typing import Dict, List, NamedTuple  # noqa: H301

import typedload
import utf8_locale


class GitTree(NamedTuple):
    """A single line in the `git ls-tree` output."""

    git_id: str
    git_type: str
    name: str


class CrateVersion(NamedTuple):
    """Cargo information about a single uploaded version of a crate."""

    name: str
    vers: str


class TestedCrate(NamedTuple):
    """A single crate to test."""

    name: str
    versions: List[str]


class Config(NamedTuple):
    """Runtime configuration for the test program."""

    cachedir: pathlib.Path
    cargo: str
    program: pathlib.Path
    utf8_env: Dict[str, str]


RE_CARGO_FETCH_HEAD = re.compile(r"^ (?P<cid> [0-9a-f]+ ) \s .*? (?P<url> \S+ ) $", re.X)

CARGO_FETCH_URL = "https://github.com/rust-lang/crates.io-index"
CARGO_CACHE_TIMEOUT = 4 * 3600

RE_GIT_TREE_LINE = re.compile(
    r""" ^
    (?P<mode> [0-7]+ ) \s+
    (?P<obj_type> [a-z]+ ) \s+
    (?P<obj_id> [0-9a-f]+ ) \s+
    (?P<name> \S .* )
    $ """,
    re.X,
)

CRATES = [
    TestedCrate(name="expect-exit", versions=["0.1.0", "0.2.0", "0.3.1", "0.4.3"]),
    TestedCrate(
        name="nom",
        versions=[
            "1.0.0-alpha2",
            "1.0.0-beta",
            "1.0.0",
            "7.0.0-alpha1",
            "7.0.0-alpha3",
            "7.0.0",
            "7.1.1",
        ],
    ),
    TestedCrate(
        name="cursed-trying-to-break-cargo",
        versions=[
            "0.0.0-Pre-Release2.7+wO30-w.8.0",
            "0.0.0",
            "1.0.0-0.HDTV-BluRay.1020p.YTSUB.L33TRip.mkv",
            "1.0.0-2.0.0-3.0.0+4.0.0-5.0.0",
            (
                "18446744073709551615.18446744073709551615.18446744073709551615"
                "---gREEAATT-.-V3R510N+--W0W.1.3-.nice"
            ),
            "18446744073709551615.18446744073709551615.18446744073709551615",
        ],
    ),
]


def find_cargo_cache() -> pathlib.Path:
    """Find the cargo cache directory."""
    home = pathlib.Path(os.environ.get("HOME", pwd.getpwuid(posix.getuid()).pw_dir))
    index = home / ".cargo/registry/index"
    for regdir in index.iterdir():
        fetch_head = regdir / ".git/FETCH_HEAD"
        if not fetch_head.is_file():
            continue

        lines = fetch_head.read_text(encoding="UTF-8").splitlines()
        if len(lines) != 1:
            sys.exit(f"Expected a single line in {fetch_head}, got {lines!r}")
        fields = RE_CARGO_FETCH_HEAD.match(lines[0])
        if not fields:
            sys.exit(f"Invalid format for the first line of {fetch_head}: {lines[0]!r}")

        if fields.group("url") == CARGO_FETCH_URL:
            return regdir

    sys.exit(f"Could not find {CARGO_FETCH_URL} in {index}")


def update_if_needed(cfg: Config) -> None:
    """Update the Cargo cache if needed."""
    lastf = cfg.cachedir / ".last-updated"
    lastupd = lastf.stat().st_mtime
    if time.time() <= lastupd + CARGO_CACHE_TIMEOUT:
        print(f"No need to update the Cargo cache at {cfg.cachedir}")
        return

    with tempfile.TemporaryDirectory() as tempd_obj:
        tempd = pathlib.Path(tempd_obj)
        print(f"Using {tempd} as a temporary directory for updating the Cargo cache")
        subprocess.check_call(
            [cfg.cargo, "install", "--root", tempd / "root", "expect-exit"], env=cfg.utf8_env
        )

    lastupd = lastf.stat().st_mtime
    if time.time() > lastupd + CARGO_CACHE_TIMEOUT:
        sys.exit(f"Could not get Cargo to update the modification time of {lastf}")


def get_crate_versions(cfg: Config, crate: str) -> List[str]:
    """Fetch some data about a crate."""

    def parse_line(line: str) -> GitTree:
        """Parse a `git ls-tree` output line."""
        mtree = RE_GIT_TREE_LINE.match(line)
        if not mtree:
            sys.exit(f"Unexpected `git ls-tree` output line: {line!r}")
        return GitTree(
            git_id=mtree.group("obj_id"), git_type=mtree.group("obj_type"), name=mtree.group("name")
        )

    def parse_tree(treeish: str) -> Dict[str, GitTree]:
        """Parse the `git ls-tree` output for the specified tree-like name."""
        lines = subprocess.check_output(
            ["git", "ls-tree", treeish], cwd=cfg.cachedir, encoding="UTF-8", env=cfg.utf8_env
        ).splitlines()
        print(f"Got {len(lines)} lines of `git ls-tree` output")
        return {tree.name: tree for tree in (parse_line(line) for line in lines)}

    def get_next_tree(treeish: str, part: str, exp_type: str) -> str:
        """Get the next part of the tree chain."""
        tree = parse_tree(treeish).get(part)
        if tree is None:
            sys.exit(f"Could not find '{part}' in the {treeish} Git tree.")
        elif tree.git_type != exp_type:
            sys.exit(f"Not a {exp_type}: {tree!r}")
        return tree.git_id

    def get_tree_id() -> str:
        """Parse the trees until we find the crate."""
        if len(crate) in (1, 2):
            parts = [str(len(crate))]
        elif len(crate) == 3:
            parts = [str(len(crate)), crate[:1]]
        else:
            parts = [crate[:2], crate[2:4]]

        return functools.reduce(
            lambda current, part: get_next_tree(current, part, "blob" if part == crate else "tree"),
            parts + [crate],
            "FETCH_HEAD",
        )

    print(f"Fetching crates.io data for {crate}")
    tree_id = get_tree_id()
    jlines = subprocess.check_output(
        ["git", "show", tree_id], cwd=cfg.cachedir, encoding="UTF-8", env=cfg.utf8_env
    ).splitlines()
    raw = [json.loads(line) for line in jlines]
    data = typedload.load(raw, List[CrateVersion])
    if any(vers.name != crate for vers in data):
        sys.exit(f"Unexpected Cargo versions: {data!r}")
    return [vers.vers for vers in data]


def parse_args() -> Config:
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser(prog="test_cargo")
    parser.add_argument(
        "-c",
        "--cargo",
        type=str,
        default="cargo",
        help="the program name (or full path) of the Cargo program to use",
    )
    parser.add_argument(
        "-p",
        "--program",
        type=pathlib.Path,
        required=True,
        help="the path to the trivver implementation to test",
    )

    args = parser.parse_args()

    return Config(
        cachedir=find_cargo_cache(),
        cargo=args.cargo,
        program=args.program,
        utf8_env=utf8_locale.UTF8Detect().detect().env,
    )


def main() -> None:
    """Parse command-line options, do stuff."""
    if os.environ.get("RUN_TRIVVER_CARGO_TEST", "0") != "1":
        print("Skipping the test, set RUN_TRIVVER_CARGO_TEST to 1 to run it")
        return

    cfg = parse_args()
    update_if_needed(cfg)

    for crate in CRATES:
        print(f"Testing {crate.name}")
        versions = get_crate_versions(cfg, crate.name)
        print(f"Got {len(versions)} versions for {crate.name}")
        missing = [vers for vers in crate.versions if vers not in versions]
        if missing:
            sys.exit(f"Cargo metadata for {crate.name} missing versions {missing!r}")

        shuffled = list(versions)
        random.shuffle(shuffled)
        res = subprocess.run(
            [cfg.program, "sort"],
            capture_output=True,
            check=True,
            encoding="UTF-8",
            env=cfg.utf8_env,
            input="".join(vers + "\n" for vers in versions),
        )
        result = res.stdout.splitlines()
        if set(result) != set(versions):
            sys.exit(
                f"`trivver sort` failed: expected {sorted(versions)!r}, got {sorted(result)!r}"
            )

        indices = [result.index(vers) for vers in crate.versions]
        if indices != sorted(indices):
            sys.exit(f"`trivver sort` did not sort the versions correctly: {indices!r}")

        print(f"Tested {crate.name} just fine!")


if __name__ == "__main__":
    main()
