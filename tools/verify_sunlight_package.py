"""Capture the real seed-one first-floor sunlight patch in source-built UZDoom."""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=int, choices=(0, 1), default=1)
    args = parser.parse_args()
    output = ROOT / "artifacts/sunlight" / ("vulkan" if args.backend else "opengl")
    output.mkdir(parents=True, exist_ok=True)
    captures = (output / "sun-rays.png", output / "broken-ceiling.png")
    for capture in captures:
        capture.unlink(missing_ok=True)
    config = output / "capture.cfg"
    config.write_text(
        "wait 350; +lookup; wait 12; -lookup; wait 5; screenshot sun-rays.png; "
        "+lookup; wait 18; -lookup; wait 5; screenshot broken-ceiling.png; wait 5; quit\n",
        encoding="ascii",
    )
    engine = ROOT / ".build/uzdoom/Release/uzdoom.exe"
    command = [
        str(engine), "-iwad", str(ROOT / ".deps/freedoom-0.13.0/freedoom2.wad"),
        "-file", str(ROOT / "mod/BrogueDoom"),
        str(ROOT / "generated/seed-1/startup/ProjectBroom-seed-1.pk3"),
        "-config", str(output / "uzdoom.ini"), "-noautoload", "-nosound", "-window",
        "-width", "1280", "-height", "720", "+set", "vid_preferbackend", str(args.backend),
        "+set", "i_pauseinbackground", "false", "+set", "brg_seed", "1",
        "+set", "brg_debug", "true", "+set", "brg_save_root", str(output / "saves"),
        "+set", "screenshot_dir", str(output), "+set", "screenblocks", "12",
        "+set", "con_notifytime", "0", "+map", "BRG01", "+exec", str(config),
    ]
    with (output / "process.log").open("w") as log:
        process = subprocess.Popen(command, cwd=output, stdout=log, stderr=subprocess.STDOUT)
        try:
            process.wait(timeout=90)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise RuntimeError(f"Sunlight capture timed out: {output}")
    log_text = (output / "process.log").read_text(errors="replace")
    if process.returncode or "Script error" in log_text or any(not path.is_file() for path in captures):
        raise RuntimeError(f"Sunlight capture failed: {output}")
    expected = "Vulkan" if args.backend else "OpenGL"
    if f"Selecting {expected} backend" not in log_text:
        raise RuntimeError(f"Requested {expected} backend was not selected: {output}")
    print(f"Sunlight capture passed: {output}")


if __name__ == "__main__":
    main()
