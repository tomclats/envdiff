"""Command line for envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff import __version__
from envdiff.diff import EnvError, labels, load_env, render_diff


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare two env files by key. Values are never printed.",
    )
    parser.add_argument("--version", action="version", version=f"envdiff {__version__}")
    parser.add_argument("left", help="First env file.")
    parser.add_argument("right", help="Second env file.")
    args = parser.parse_args(argv)
    try:
        left = load_env(Path(args.left))
        right = load_env(Path(args.right))
        left_label, right_label = labels(args.left, args.right)
        sys.stdout.write(render_diff(left_label, left, right_label, right))
    except EnvError as exc:
        print(f"envdiff: {exc}", file=sys.stderr)
        return 1
    return 0
