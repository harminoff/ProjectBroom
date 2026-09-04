#!/usr/bin/env python3
"""Build a development-only map with visible Project Broom water, sludge, and lava."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mapcompiler.compile import compile_package
from tools.mapcompiler.test_compile import sample_model


OUTPUT_DIR = ROOT / "artifacts" / "cc4-runtime"


def main() -> int:
    model = sample_model()
    model["terrainCatalog"].extend([
        {"id": 3, "symbol": "DEEP_WATER"},
        {"id": 4, "symbol": "LAVA"},
        {"id": 5, "symbol": "MUD"},
    ])
    for cell in model["levels"][0]["cells"]:
        x, y = cell["x"], cell["y"]
        if x in (0, 78) or y in (0, 28):
            continue
        if x < 27:
            cell["layers"]["liquid"] = {"id": 3, "symbol": "DEEP_WATER"}
        elif x < 53:
            cell["layers"]["liquid"] = {"id": 5, "symbol": "MUD"}
        else:
            cell["layers"]["liquid"] = {"id": 4, "symbol": "LAVA"}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    input_path = OUTPUT_DIR / "liquid-smoke.json"
    package_path = OUTPUT_DIR / "liquid-smoke.pk3"
    input_path.write_text(json.dumps(model, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    compile_package(input_path, package_path, depth=1, map_name="MAP01")
    print(json.dumps({"input": str(input_path), "package": str(package_path)}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
