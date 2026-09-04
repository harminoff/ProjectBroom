#!/usr/bin/env python3
"""Write human-readable per-depth Brogue snapshot artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _semantic(cell: dict[str, Any], name: str) -> bool:
    semantic = cell.get("semantic")
    if isinstance(semantic, dict) and isinstance(semantic.get(name), bool):
        return semantic[name]
    return False


def cell_glyph(cell: dict[str, Any]) -> str:
    dungeon = str(cell["layers"]["dungeon"]["symbol"])
    liquid = str(cell["layers"]["liquid"]["symbol"])
    surface = str(cell["layers"]["surface"]["symbol"])

    if _semantic(cell, "isStairsUp") or dungeon in {"UP_STAIRS", "DUNGEON_EXIT"}:
        return "<"
    if _semantic(cell, "isStairsDown") or dungeon in {"DOWN_STAIRS", "DUNGEON_PORTAL"}:
        return ">"
    if _semantic(cell, "isDoor") or "DOOR" in dungeon or "PORTCULLIS" in dungeon:
        return "+"
    if _semantic(cell, "isBridge") or liquid in {"BRIDGE", "BRIDGE_FALLING"} or surface in {"BRIDGE_EDGE", "STONE_BRIDGE"}:
        return "="
    if _semantic(cell, "isLava") or liquid in {"LAVA", "LAVA_RETRACTABLE", "LAVA_RETRACTING", "SACRIFICE_LAVA"}:
        return "^"
    if _semantic(cell, "isChasm") or liquid in {"CHASM", "CHASM_EDGE", "CHASM_WITH_HIDDEN_BRIDGE", "CHASM_WITH_HIDDEN_BRIDGE_ACTIVE"}:
        return "_"
    if _semantic(cell, "isLiquid") or liquid != "NOTHING":
        return "~"
    if _semantic(cell, "isSolid") or dungeon in {"GRANITE", "WALL", "CRYSTAL_WALL", "MUD_WALL"}:
        return "#"
    if surface in {"GRASS", "DEAD_GRASS", "FOLIAGE", "DEAD_FOLIAGE", "FUNGUS_FOREST", "TRAMPLED_FOLIAGE", "TRAMPLED_FUNGUS_FOREST"}:
        return ","
    return "."


def ascii_level(level: dict[str, Any]) -> str:
    width = int(level["width"])
    height = int(level["height"])
    cells = {(int(cell["x"]), int(cell["y"])): cell for cell in level["cells"]}
    lines = [
        f"seed={level['gameSeed']} levelSeed={level['levelSeed']} depth={level['depth']}",
        f"up={level['upStairs']['x']},{level['upStairs']['y']} down={level['downStairs']['x']},{level['downStairs']['y']}",
    ]
    lines.extend("".join(cell_glyph(cells[(x, y)]) for x in range(width)) for y in range(height))
    return "\n".join(lines) + "\n"


def level_projection(model: dict[str, Any], level: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": model.get("schemaVersion"),
        "source": model.get("source", {}),
        "gameSeed": str(model.get("seed", "")),
        "levelSeed": str(level["levelSeed"]),
        "depth": int(level["depth"]),
        "width": int(model["dimensions"]["width"]),
        "height": int(model["dimensions"]["height"]),
        "upStairs": level["upStairs"],
        "downStairs": level["downStairs"],
        "terrainCatalog": model.get("terrainCatalog", []),
        "cells": level["cells"],
        "entities": level.get("entities", {"items": [], "monsters": []}),
    }


def write_level_artifacts(model: dict[str, Any], depth: int, output_root: Path) -> tuple[Path, Path]:
    if depth < 1 or depth > len(model["levels"]):
        raise ValueError(f"depth {depth} is outside the exported level range")
    level = model["levels"][depth - 1]
    depth_root = output_root / f"depth-{depth}"
    depth_root.mkdir(parents=True, exist_ok=True)
    projection = level_projection(model, level)
    json_path = depth_root / "level.json"
    txt_path = depth_root / "level.txt"
    json_path.write_text(json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_path.write_text(ascii_level(projection), encoding="utf-8")
    return json_path, txt_path
