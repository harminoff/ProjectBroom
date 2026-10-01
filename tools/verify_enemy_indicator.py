"""Capture a natural seed-one rat while rotating it across both HUD edges."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTE = " ".join(["N"] * 3 + ["W"] * 25 + ["N"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    output = ROOT / "artifacts/enemy-indicator-smoke" / ("vulkan" if args.backend else "opengl")
    output.mkdir(parents=True, exist_ok=True)
    captures = tuple(output / name for name in ("initial.png", "turned-left.png", "turned-right.png"))
    for capture in captures:
        capture.unlink(missing_ok=True)
    config = output / "capture.cfg"
    config.write_text(
        "brg_debug true; screenblocks 12; con_notifytime 0; brg_enemy_walk_tics 5; "
        f"wait 100; brg_actions {ROUTE}; wait 700; brg_monsters; "
        "screenshot initial.png; +left; wait 35; -left; wait 5; screenshot turned-left.png; "
        "+right; wait 70; -right; wait 5; screenshot turned-right.png; wait 5; quit\n",
        encoding="ascii",
    )
    command = [
        str(ROOT / ".build/uzdoom/Release/uzdoom.exe"),
        "-iwad", str(ROOT / ".deps/freedoom-0.13.0/freedoom2.wad"),
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
            raise RuntimeError(f"Enemy indicator capture timed out: {output}")
    log_text = (output / "process.log").read_text(errors="replace")
    if process.returncode or "Script error" in log_text or any(not path.is_file() for path in captures):
        raise RuntimeError(f"Enemy indicator capture failed: {output}")
    expected = "Vulkan" if args.backend else "OpenGL"
    if f"Selecting {expected} backend" not in log_text:
        raise RuntimeError(f"Requested {expected} backend was not selected: {output}")
    print(f"Enemy indicator capture passed: {output}")


if __name__ == "__main__":
    main()
