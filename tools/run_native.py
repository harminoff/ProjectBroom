"""Run native build tools with a case-insensitive Windows environment."""
import os
import subprocess
import sys


def main():
    # Windows environment blocks are case-insensitive, but .NET's
    # ProcessStartInfo can still observe duplicate entries when a parent
    # process supplies both `PATH` and `Path`. Keep one canonical spelling so
    # MSBuild can construct its child environment without throwing on a
    # duplicate dictionary key.
    environment = {
        key: value for key, value in os.environ.items() if key.lower() != "path"
    }
    environment["Path"] = os.environ.get("PATH", os.environ.get("Path", ""))
    environment["MSBUILDDISABLENODEREUSE"] = "1"
    return subprocess.call(sys.argv[1:], env=environment)


if __name__ == "__main__":
    raise SystemExit(main())
