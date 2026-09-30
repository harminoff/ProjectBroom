"""Capture explorer dressing from the normal player camera on seed one."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
# From the authoritative upstairs at (38, 27) to the open cell immediately
# north of the creature-den set piece at (5, 24). The route avoids chasms,
# lava, and deep water in the exported authoritative terrain.
ROUTE = " ".join(
    ["W"] * 10
    + ["N"] * 3
    + ["W"] * 23
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    output = ROOT / "artifacts/explorer-setpieces" / ("vulkan" if args.backend else "opengl")
    output.mkdir(parents=True, exist_ok=True)
    capture = output / "creature-den-player-view-close.png"
    capture.unlink(missing_ok=True)
    config = output / "capture.cfg"
    config.write_text(
        "brg_debug true; screenblocks 12; con_notifytime 0; brg_enemy_walk_tics 5; "
        f"wait 100; brg_actions {ROUTE}; wait 1800; "
        "+right; wait 35; -right; +lookdown; wait 12; -lookdown; wait 8; "
        f'screenshot "{capture.as_posix()}"; wait 5; quit\n',
        encoding="ascii",
    )
    command = [
        str(ROOT / ".build/uzdoom/Release/uzdoom.exe"),
        "-iwad", str(ROOT / ".deps/freedoom-0.13.0/freedoom2.wad"),
        "-file", str(ROOT / "mod/BrogueDoom"),
        str(ROOT / "artifacts/explorer-setpieces/ProjectBroom-seed-1.pk3"),
        "-config", str(output / "uzdoom.ini"), "-noautoload", "-nosound", "-window",
        "-width", "1280", "-height", "720", "+set", "vid_preferbackend", str(args.backend),
        "+set", "i_pauseinbackground", "false", "+set", "brg_seed", "1",
        "+set", "brg_save_root", str(output / "fresh-saves-v5"),
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
            raise RuntimeError(f"Explorer set-piece capture timed out: {output}")
    log_text = (output / "process.log").read_text(errors="replace")
    if process.returncode or "Script error" in log_text or not capture.is_file():
        raise RuntimeError(f"Explorer set-piece capture failed: {output}")
    expected = "Vulkan" if args.backend else "OpenGL"
    if f"Selecting {expected} backend" not in log_text:
        raise RuntimeError(f"Requested {expected} backend was not selected: {output}")
    if "scripted action queue complete" not in log_text:
        raise RuntimeError(f"Explorer route did not complete: {output}")
    print(f"Explorer set-piece capture passed: {capture}")


if __name__ == "__main__":
    main()
