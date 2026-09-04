#!/usr/bin/env python3
"""Generate the non-interactive Brogue door presentation model."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "mod" / "BrogueDoom" / "models" / "doors" / "door_panel.obj"

# Crop the framed wooden door from BRGDOOR0.png without duplicating the source
# image. OBJ V coordinates run bottom-to-top, unlike PNG pixel coordinates.
IMAGE_SIZE = 1254.0
U0 = 340.0 / IMAGE_SIZE
U1 = 914.0 / IMAGE_SIZE
V0 = 1.0 - 1218.0 / IMAGE_SIZE
V1 = 1.0 - 38.0 / IMAGE_SIZE


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "o BrogueDoorPanel",
        # GZDoom maps OBJ X to actor-forward, Y to world-up, and Z lateral.
        # The panel fills a Brogue portal while leaving a small stone reveal.
        "v -2 0 -30",
        "v 2 0 -30",
        "v 2 124 -30",
        "v -2 124 -30",
        "v -2 0 30",
        "v 2 0 30",
        "v 2 124 30",
        "v -2 124 30",
        f"vt {U0:.9f} {V0:.9f}",
        f"vt {U1:.9f} {V0:.9f}",
        f"vt {U1:.9f} {V1:.9f}",
        f"vt {U0:.9f} {V1:.9f}",
        # Both broad faces use the cropped framed-door artwork. Thin edges use
        # the same crop; they are mostly hidden inside the doorway reveal.
        "f 1/1 4/4 3/3 2/2",
        "f 5/1 6/2 7/3 8/4",
        "f 1/1 2/2 6/3 5/4",
        "f 2/1 3/2 7/3 6/4",
        "f 3/1 4/2 8/3 7/4",
        "f 4/1 1/2 5/3 8/4",
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
