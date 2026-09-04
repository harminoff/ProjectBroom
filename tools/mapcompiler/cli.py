#!/usr/bin/env python3
"""Packaged Project Broom map compiler and verifier command line."""

from __future__ import annotations

import argparse
import sys

from tools.mapcompiler import compile as compiler
from tools.mapcompiler import verify


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("compile", "verify"))
    args, remaining = parser.parse_known_args(argv)
    if args.command == "compile":
        return compiler.main(remaining)
    return verify.main(remaining)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
