"""Opt-in real chasm fall capture; requires the source build and seed-1 startup PK3."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = "N N N N N N N N N W W W W W W N N N N N W N W W N N N N N"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=int, choices=(0, 1), required=True)
    args = parser.parse_args()
    out = ROOT / "artifacts/chasm-transition" / f"verified-{args.backend}"
    out.mkdir(parents=True, exist_ok=True)
    cfg = ["brg_debug true", "screenblocks 12", "con_notifytime 0", "wait 100",
           "brg_actions " + ACTIONS, "wait 1000", "screenshot brink.png",
           "brg_confirm no", "wait 35", "screenshot cancelled.png",
           "brg_actions N", "wait 70", "brg_confirm yes",
           "wait 8", "screenshot departure.png", "wait 10", "screenshot dark.png",
           "wait 10", "screenshot arrival.png", "wait 80", "screenshot landed.png", "quit"]
    (out / "capture.cfg").write_text("; ".join(cfg) + "\n")
    cmd = [str(ROOT / ".build/uzdoom/Release/uzdoom.exe"),
           "-iwad", str(ROOT / ".deps/freedoom-0.13.0/freedoom2.wad"),
           "-file", str(ROOT / "mod/BrogueDoom"),
           str(ROOT / "generated/seed-1/startup/ProjectBroom-seed-1.pk3"),
           "-config", str(out / "test.ini"), "-noautoload", "-nosound", "-window",
           "+set", "vid_preferbackend", str(args.backend),
           "+set", "i_pauseinbackground", "false",
           "+set", "brg_save_root", str(out / "saves"),
           "+set", "brg_map_compiler", sys.executable,
           "+set", "brg_map_compiler_root", str(ROOT), "+set", "brg_seed", "1",
           "+set", "screenshot_dir", str(out), "+map", "BRG01",
           "+exec", str(out / "capture.cfg")]
    environment = {key.upper(): value for key, value in os.environ.items()}
    with (out / "runtime.log").open("w") as log:
        result = subprocess.run(cmd, cwd=out, env=environment, stdout=log,
                                stderr=subprocess.STDOUT, timeout=120)
    text = (out / "runtime.log").read_text(errors="replace")
    assert result.returncode == 0, text[-3000:]
    assert "Selecting " + ("Vulkan" if args.backend else "OpenGL") + " backend" in text
    assert text.count("Brogue fall transition: departing.") == 1
    assert text.count("Brogue fall transition: arriving.") == 1
    # Same seed/actions on the pre-transition executable, including damage and
    # landing. No additional turn or RNG changes while presenting the fall.
    assert "Brogue fall transition: complete turn=28 hash=16b7f15d918ac047." in text
    assert "SAVE_BEGIN turn=29 depth=2 hash=16b7f15d918ac047" in text
    assert "Brogue bridge: fall shaft landing=28,5" in text
    assert text.index("Captured cancelled.png") < text.index("Brogue fall transition: departing.")
    for name in ("brink", "cancelled", "departure", "dark", "arrival", "landed"):
        assert (out / f"{name}.png").is_file()
    print("Chasm transition passed:", out)


if __name__ == "__main__":
    main()
