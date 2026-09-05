"""Validate the complete pinned engine patch without replacing local work."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ENGINE_FILES = ("uzdoom.exe", "uzdoom.pk3", "game_support.pk3",
                "game_widescreen_gfx.pk3", "brightmaps.pk3", "lights.pk3")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_record(root, engine):
    validate(root)
    inputs = ("dependencies.lock.json", "patches/uzdoom-project-broom.patch",
              "src/gzdoom-bridge/brogue_bridge_frontend.cpp",
              "src/gzdoom-bridge/brogue_bridge_frontend.h",
              "src/brogue-mapgen/src/brogue/BrogueBridge.h")
    return {"schemaVersion": 1,
            "inputs": {name: digest(root / name) for name in inputs},
            "outputs": {name: digest(engine / name) for name in ENGINE_FILES}}


def validate_build(root, engine):
    recorded = json.loads((engine / "project-broom-build.json").read_text())
    if recorded != build_record(root, engine):
        raise ValueError("Engine build is stale or modified; run scripts/build-dev.ps1")


def validate(root: Path, apply: bool = False):
    component = json.loads((root / "dependencies.lock.json").read_text())["components"]["uzdoom"]
    checkout = root / ".deps/uzdoom-source"
    patch = root / component["patch"]
    if hashlib.sha256(patch.read_bytes()).hexdigest() != component["patchSha256"]:
        raise ValueError("UZDoom patch hash does not match the lockfile")

    def git(*args):
        return subprocess.run(["git", "-C", str(checkout), *args], check=True,
                              capture_output=True, text=True).stdout

    if git("rev-parse", "HEAD").strip() != component["commit"]:
        raise ValueError("UZDoom checkout does not match the pinned commit")
    if apply and not git("status", "--porcelain").strip():
        git("apply", "--check", str(patch.resolve()))
        git("apply", str(patch.resolve()))
    # Force full object IDs so validation is independent of each checkout's
    # core.abbrev setting.
    actual = git("diff", "--no-ext-diff", "--binary", "--full-index").strip()
    if (actual != patch.read_text().strip()
            or git("diff", "--cached", "--name-only").strip()
            or git("ls-files", "--others", "--exclude-standard").strip()):
        raise ValueError("UZDoom differs from the complete pinned integration patch; preserve local edits")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--record-build", type=Path)
    args = parser.parse_args()
    validate(args.root, args.apply)
    if args.record_build:
        record = build_record(args.root, args.record_build)
        (args.record_build / "project-broom-build.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Pinned UZDoom source and integration patch verified.")
