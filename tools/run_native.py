"""Run native build tools with a case-insensitive Windows environment."""
import os
import subprocess
import sys


def main():
    environment = {key.upper(): value for key, value in os.environ.items()}
    environment["MSBUILDDISABLENODEREUSE"] = "1"
    return subprocess.call(sys.argv[1:], env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
