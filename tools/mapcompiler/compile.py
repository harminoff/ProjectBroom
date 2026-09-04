#!/usr/bin/env python3
"""Compile Brogue terrain JSON into deterministic UDMF map WADs and a PK3."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import zipfile
from pathlib import Path
from typing import Any, Collection, Iterable

if os.environ.get("PROJECTBROOM_RESOURCE_ROOT"):
    PROJECT_ROOT = Path(os.environ["PROJECTBROOM_RESOURCE_ROOT"]).resolve()
elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PROJECT_ROOT = Path(sys._MEIPASS).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CELL_SIZE = 64
# Chasms are a visual recess, not a literal 512-unit shaft in the Doom map.
# A very deep sector makes its lower sidedefs dominate the view and read as
# full-height black columns when a room is visible across the opening. Brogue
# still owns falling and level transitions; this depth only presents a dark,
# bounded cave opening beneath the unchanged cell portal.
CHASM_FLOOR_Z = -128
CHASM_LIGHT_LEVEL = 144
CHASM_PORTAL_DEPTH = 10
CHASM_PORTAL_SHOULDER = 14
OPEN_VOID_CEILING_Z = 224
OPEN_VOID_SKY_FLAT = "F_SKY1"
OPEN_VOID_SKY_TEXTURE = "BRGSKY"
EXPECTED_WIDTH = 79
EXPECTED_HEIGHT = 29
EXPECTED_SECTORS = EXPECTED_WIDTH * EXPECTED_HEIGHT
EXPECTED_VERTICES = (EXPECTED_WIDTH + 1) * (EXPECTED_HEIGHT + 1)
CONTOUR_DEPTH = 8
CONTOUR_SHOULDER = 12
CONTOUR_MIN_RUN = 3
CONTOUR_RUN_STRIDE = 4
COMPILER_VERSION = "37"
RENDER_MAPPING_PATH = Path(__file__).with_name("terrain_render_map.json")
THEME_REGISTRY_PATH = PROJECT_ROOT / "assets" / "terrain" / "broguedoom_cave_registry.json"
RESOURCE_GRAPHICS_DIR = PROJECT_ROOT / "mod" / "BrogueDoom" / "graphics"
RESOURCE_MOD_DIR = PROJECT_ROOT / "mod" / "BrogueDoom"
RESOURCE_ASSET_FILES = (
    "BRGROCK.png",
    "BRGDIRT.png",
    "BRGSTONE.png",
    "BRGBRIDGE.png",
    "BRGWATER.png",
    "BRGLAVA.png",
    "BRGLAVA_BM.png",
    "BRGVEG0.png",
    "BRGDOOR0.png",
    "BRGUSTA.png",
    "BRGDSTA.png",
    "BRGPIT.png",
    "BRGCLIFF.png",
)
RESOURCE_PRESENTATION_FILES = (
    "MODELDEF",
    "GLDEFS",
    "brogue_fx.zs",
    "models/doors/door_panel.obj",
    "models/doors/wooden_barricade.obj",
    "models/stairs/upstairs.obj",
    "models/stairs/up_hatch.obj",
    "models/stairs/downstairs.obj",
    "models/stairs/down_void.obj",
    "models/stairs/fall_shaft.obj",
)
CUSTOM_TEXTURES = {"BRGCAVE", "BRGWET", "BRGMASON", "BRGDOOR", "BRGWFALL", "BRGLFALL", "BRGVOID", "BRGCLIFF", "BRGSKY"}
CUSTOM_FLATS = {"BRGEARTH", "BRGCEIL", "BRGMOSS", "BRGFLAG", "BRGBRID", "BRGWATR", "BRGSLDG", "BRGMOLT", "BRGCHASM", "BRGABYSS"}

PROP_RULES: dict[str, tuple[str, int, int]] = {
    # surface symbol: (presentation role, DoomEdNum, one placement per N cells)
    "GRASS": ("grass", 15010, 4),
    "ANCIENT_SPIRIT_GRASS": ("grass", 15010, 2),
    "FUNGUS_FOREST": ("fungus", 15011, 3),
    "TRAMPLED_FUNGUS_FOREST": ("fungus", 15011, 4),
    "GRAY_FUNGUS": ("fungus", 15011, 3),
    "LUMINESCENT_FUNGUS": ("luminous_fungus", 15012, 3),
    "FOLIAGE": ("foliage", 15013, 1),
    "TRAMPLED_FOLIAGE": ("foliage", 15013, 4),
    "DEAD_GRASS": ("dead_vegetation", 15014, 5),
    "DEAD_FOLIAGE": ("dead_vegetation", 15014, 3),
}
VEGETATED_FLOOR_SURFACES = {
    "GRASS",
    "ANCIENT_SPIRIT_GRASS",
    "FOLIAGE",
    "TRAMPLED_FOLIAGE",
    "FUNGUS_FOREST",
    "TRAMPLED_FUNGUS_FOREST",
    "GRAY_FUNGUS",
    "LUMINESCENT_FUNGUS",
    "LICHEN",
}

PASSABILITY_BLOCKER = 1
AUTO_DESCENT = 1 << 7
WALL_SYMBOLS = {
    "GRANITE",
    "WALL",
    "SECRET_DOOR",
    "LOCKED_DOOR",
    "CRYSTAL_WALL",
    "PORTCULLIS_CLOSED",
    "PORTCULLIS_DORMANT",
    "WOODEN_BARRICADE",
    "MUD_WALL",
    "WORM_TUNNEL_OUTER_WALL",
}
DOOR_CLOSED_SYMBOLS = {
    "DOOR",
    "SECRET_DOOR",
    "LOCKED_DOOR",
    "PORTCULLIS_CLOSED",
    "PORTCULLIS_DORMANT",
    "WOODEN_BARRICADE",
}
DOOR_GEOMETRY_SYMBOLS = DOOR_CLOSED_SYMBOLS | {
    "OPEN_DOOR",
    "OPEN_IRON_DOOR_INERT",
    "MUD_DOORWAY",
    "STATUE_INERT_DOORWAY",
    "STATUE_DORMANT_DOORWAY",
}
# Kept as the wall/material classification used by existing call sites.
DOOR_SYMBOLS = DOOR_CLOSED_SYMBOLS

ANIMATED_FLAT_BASES = {
    "fwater1": "fwater1",
    "fwater2": "fwater1",
    "fwater3": "fwater1",
    "fwater4": "fwater1",
    "slime01": "slime01",
    "slime02": "slime01",
    "slime03": "slime01",
    "slime04": "slime01",
    "lava1": "lava1",
    "lava2": "lava1",
    "lava3": "lava1",
    "lava4": "lava1",
    "brgwatr": "brgwatr",
    "brgsldg": "brgsldg",
    "brgmolt": "brgmolt",
}


class CompileError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resource_pack_hash() -> str:
    digest = hashlib.sha256()
    paths = (
        [THEME_REGISTRY_PATH]
        + [RESOURCE_GRAPHICS_DIR / name for name in RESOURCE_ASSET_FILES]
        + [RESOURCE_MOD_DIR / name for name in RESOURCE_PRESENTATION_FILES]
    )
    for path in paths:
        if not path.is_file():
            raise RuntimeError(f"required Project Broom texture asset is missing: {path}")
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_render_mapping() -> dict[str, dict[str, Any]]:
    try:
        mapping = json.loads(RENDER_MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"could not load terrain render mapping: {error}") from error
    if not isinstance(mapping, dict):
        raise RuntimeError("terrain render mapping root is not an object")
    return mapping


TERRAIN_RENDER_MAP = load_render_mapping()


def load_theme_registry() -> dict[str, Any]:
    try:
        registry = json.loads(THEME_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"could not load terrain theme registry: {error}") from error
    if not isinstance(registry, dict) or registry.get("schemaVersion") != 1:
        raise RuntimeError("terrain theme registry must have schemaVersion 1")
    themes = registry.get("themes")
    if not isinstance(themes, dict) or not themes:
        raise RuntimeError("terrain theme registry has no themes")
    resource_pack_hash()
    animations = registry.get("animations")
    if not isinstance(animations, dict) or not animations:
        raise RuntimeError("terrain theme registry has no animations")
    inherited_frames: set[str] = set()
    for animation_name, animation in animations.items():
        if not isinstance(animation, dict) or animation.get("kind") != "flat":
            raise RuntimeError(f"animation {animation_name} is invalid")
        frames = animation.get("frames")
        if not isinstance(frames, list) or not frames or not all(isinstance(frame, str) and frame for frame in frames):
            raise RuntimeError(f"animation {animation_name} has invalid frames")
        if animation.get("base") != frames[0]:
            raise RuntimeError(f"animation {animation_name} base must be its first frame")
        inherited_frames.update(frame.upper() for frame in frames)
    for theme_name, theme in themes.items():
        if not isinstance(theme_name, str) or not isinstance(theme, dict):
            raise RuntimeError("terrain theme registry contains an invalid theme")
        for role in ("walls", "floors", "ceilings"):
            assets = theme.get(role)
            if not isinstance(assets, list) or not assets or not all(isinstance(asset, str) and asset for asset in assets):
                raise RuntimeError(f"theme {theme_name} has invalid {role}")
            if role == "floors":
                for asset in assets:
                    animation_base = ANIMATED_FLAT_BASES.get(asset.lower())
                    if animation_base is not None and asset.lower() != animation_base:
                        raise RuntimeError(
                            f"theme {theme_name} uses animation frame {asset} instead of base {animation_base}"
                        )
            available = CUSTOM_TEXTURES if role == "walls" else CUSTOM_FLATS
            for asset in assets:
                if asset.upper() not in available and asset.upper() not in inherited_frames:
                    raise RuntimeError(f"theme {theme_name} references unknown Project Broom {role[:-1]}: {asset}")
        if not isinstance(theme.get("door"), str) or not theme["door"]:
            raise RuntimeError(f"theme {theme_name} has no door texture")
        if theme["door"].upper() not in CUSTOM_TEXTURES:
            raise RuntimeError(f"theme {theme_name} door is absent from Project Broom resources: {theme['door']}")
        if "fall" in theme and str(theme["fall"]).upper() not in CUSTOM_TEXTURES:
            raise RuntimeError(f"theme {theme_name} fall texture is absent from Project Broom resources: {theme['fall']}")
    default_theme = registry.get("defaultTheme")
    if default_theme not in themes:
        raise RuntimeError("terrain theme registry defaultTheme is unknown")
    if registry.get("variantScope") != "semantic-region":
        raise RuntimeError("terrain theme registry variantScope must be semantic-region")
    surface_tints = registry.get("surfaceTints")
    if not isinstance(surface_tints, dict):
        raise RuntimeError("terrain theme registry surfaceTints must be an object")
    for symbol, tint in surface_tints.items():
        if not isinstance(symbol, str) or isinstance(tint, bool) or not isinstance(tint, int) or not 0 <= tint <= 0xFFFFFF:
            raise RuntimeError("terrain theme registry contains an invalid surface tint")
    for rule in registry.get("rules", []) + registry.get("adjacencyRules", []):
        if not isinstance(rule, dict) or rule.get("theme") not in themes:
            raise RuntimeError("terrain theme registry rule references an unknown theme")
    return registry


TERRAIN_THEME_REGISTRY = load_theme_registry()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def text(value: str) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def int_field(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CompileError(f"{field} must be an integer")
    return value


def validate_model(model: dict[str, Any]) -> tuple[int, int, dict[int, str]]:
    if model.get("schemaVersion") != 1:
        raise CompileError("unsupported JSON schemaVersion")
    dimensions = model.get("dimensions")
    if not isinstance(dimensions, dict):
        raise CompileError("dimensions is required")
    width = int_field(dimensions.get("width"), "dimensions.width")
    height = int_field(dimensions.get("height"), "dimensions.height")
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise CompileError(f"expected Brogue dimensions {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}, got {width}x{height}")

    catalog: dict[int, str] = {}
    for record in model.get("terrainCatalog", []):
        if not isinstance(record, dict):
            raise CompileError("terrain catalog record is not an object")
        tile_id = int_field(record.get("id"), "terrainCatalog.id")
        symbol = record.get("symbol")
        if not isinstance(symbol, str) or not symbol:
            raise CompileError(f"terrainCatalog[{tile_id}] has no symbol")
        if tile_id in catalog and catalog[tile_id] != symbol:
            raise CompileError(f"conflicting symbol for terrain id {tile_id}")
        catalog[tile_id] = symbol
    if not catalog:
        raise CompileError("terrainCatalog is empty")
    for symbol in catalog.values():
        if symbol not in TERRAIN_RENDER_MAP:
            raise CompileError(f"terrain symbol has no render mapping: {symbol}")

    levels = model.get("levels")
    if not isinstance(levels, list) or not levels:
        raise CompileError("levels is empty")
    expected_depths = list(range(1, len(levels) + 1))
    actual_depths = [int_field(level.get("depth"), "level.depth") for level in levels if isinstance(level, dict)]
    if actual_depths != expected_depths:
        raise CompileError("levels must be ordered and numbered from depth 1")

    for level in levels:
        if not isinstance(level, dict):
            raise CompileError("level is not an object")
        cells = level.get("cells")
        if not isinstance(cells, list) or len(cells) != EXPECTED_SECTORS:
            raise CompileError(f"depth {level.get('depth')} must contain {EXPECTED_SECTORS} cells")
        seen: set[tuple[int, int]] = set()
        for cell in cells:
            if not isinstance(cell, dict):
                raise CompileError("cell is not an object")
            x = int_field(cell.get("x"), "cell.x")
            y = int_field(cell.get("y"), "cell.y")
            if not (0 <= x < width and 0 <= y < height):
                raise CompileError(f"cell coordinate out of bounds: {x},{y}")
            if (x, y) in seen:
                raise CompileError(f"duplicate cell coordinate: {x},{y}")
            seen.add((x, y))
            layers = cell.get("layers")
            if not isinstance(layers, dict):
                raise CompileError("cell.layers is required")
            for layer_name in ("dungeon", "liquid", "gas", "surface"):
                layer = layers.get(layer_name)
                if not isinstance(layer, dict):
                    raise CompileError(f"cell layer {layer_name} is missing")
                tile_id = int_field(layer.get("id"), f"cell.layers.{layer_name}.id")
                symbol = layer.get("symbol")
                if tile_id not in catalog:
                    raise CompileError(f"cell references unknown terrain id {tile_id}")
                if symbol != catalog[tile_id]:
                    raise CompileError(f"terrain symbol mismatch for id {tile_id}")
        if len(seen) != EXPECTED_SECTORS:
            raise CompileError(f"depth {level.get('depth')} has missing cells")
        for stair_name in ("upStairs", "downStairs"):
            stair = level.get(stair_name)
            if not isinstance(stair, dict):
                raise CompileError(f"depth {level.get('depth')} has no {stair_name}")
            sx = int_field(stair.get("x"), f"{stair_name}.x")
            sy = int_field(stair.get("y"), f"{stair_name}.y")
            if not (0 <= sx < width and 0 <= sy < height):
                raise CompileError(f"depth {level.get('depth')} {stair_name} is out of bounds")

    return width, height, catalog


def world_vertex_index(width: int, grid_x: int, grid_y: int) -> int:
    return grid_y * (width + 1) + grid_x


def world_y(height: int, grid_y: int) -> int:
    return (height - grid_y) * CELL_SIZE


def cell_center(width: int, height: int, x: int, y: int) -> tuple[int, int]:
    del width
    return x * CELL_SIZE + CELL_SIZE // 2, (height - y - 1) * CELL_SIZE + CELL_SIZE // 2


def cell_sides(width: int, height: int, x: int, y: int) -> list[tuple[int, int]]:
    tl = world_vertex_index(width, x, y)
    tr = world_vertex_index(width, x + 1, y)
    br = world_vertex_index(width, x + 1, y + 1)
    bl = world_vertex_index(width, x, y + 1)
    return [(tl, tr), (tr, br), (br, bl), (bl, tl)]


def cell_side_coordinates(height: int, x: int, y: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Return clockwise world-coordinate edges for a Brogue cell."""
    top = world_y(height, y)
    bottom = world_y(height, y + 1)
    left = x * CELL_SIZE
    right = (x + 1) * CELL_SIZE
    tl = (left, top)
    tr = (right, top)
    br = (right, bottom)
    bl = (left, bottom)
    return [(tl, tr), (tr, br), (br, bl), (bl, tl)]


def contoured_side_points(
    height: int,
    x: int,
    y: int,
    side_index: int,
    *,
    contoured: bool,
    depth: int = CONTOUR_DEPTH,
    shoulder: int = CONTOUR_SHOULDER,
) -> list[tuple[int, int]]:
    """Return an exact portal edge or a topology-safe wall recess.

    Traversable-to-traversable portals stay on the Brogue grid. A solid
    boundary gains two angled shoulders and a middle segment recessed into
    the solid neighbor. Original corners stay fixed, so adjacent loops close
    exactly and diagonally touching open cells still meet at only one point.
    """
    start, end = cell_side_coordinates(height, x, y)[side_index]
    if not contoured:
        return [start, end]
    outward = ((0, depth), (depth, 0), (0, -depth), (-depth, 0))[side_index]
    dx = (end[0] - start[0]) // CELL_SIZE
    dy = (end[1] - start[1]) // CELL_SIZE
    first = (
        start[0] + dx * shoulder + outward[0],
        start[1] + dy * shoulder + outward[1],
    )
    second_distance = CELL_SIZE - shoulder
    second = (
        start[0] + dx * second_distance + outward[0],
        start[1] + dy * second_distance + outward[1],
    )
    return [start, first, second, end]


def boundary_uses_contour(
    geometry_cells: Collection[tuple[int, int]],
    x: int,
    y: int,
    side_index: int,
) -> bool:
    """Select sparse recesses inside long, straight solid boundaries.

    Short and irregular walls remain straight. On a continuous run, only one
    interior cell in every four is recessed, preventing the 64-unit grid from
    turning into a repeated scallop pattern.
    """
    neighbor_steps = ((0, -1), (1, 0), (0, 1), (-1, 0))
    dx, dy = neighbor_steps[side_index]

    def is_boundary(position: tuple[int, int]) -> bool:
        px, py = position
        return position in geometry_cells and (px + dx, py + dy) not in geometry_cells

    if not is_boundary((x, y)):
        return False
    run_step = (1, 0) if side_index in (0, 2) else (0, 1)
    start_x, start_y = x, y
    while is_boundary((start_x - run_step[0], start_y - run_step[1])):
        start_x -= run_step[0]
        start_y -= run_step[1]
    run_length = 1
    while is_boundary((start_x + run_step[0] * run_length, start_y + run_step[1] * run_length)):
        run_length += 1
    run_index = (x - start_x) if run_step[0] else (y - start_y)
    return (
        run_length >= CONTOUR_MIN_RUN
        and 0 < run_index < run_length - 1
        and (run_index - 1) % CONTOUR_RUN_STRIDE == 0
    )


def is_chasm_portal(
    cell: dict[str, Any],
    neighbor: dict[str, Any] | None,
    cells: dict[tuple[int, int], dict[str, Any]],
) -> bool:
    """Return true for a ground-to-abyss portal that may receive a visual lip."""
    if neighbor is None:
        return False
    if cell_is_chasm_bridge(cell, cells) or cell_is_chasm_bridge(neighbor, cells):
        return False
    return cell_is_chasm_void(cell) != cell_is_chasm_void(neighbor)


def map_side_points(
    height: int,
    x: int,
    y: int,
    side_index: int,
    cell: dict[str, Any],
    neighbor: dict[str, Any] | None,
    cells: dict[tuple[int, int], dict[str, Any]],
    geometry_cells: Collection[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return the shared visual boundary while preserving cardinal topology.

    Solid walls retain the sparse cave contour. Ground-to-chasm portals gain a
    shallow recess into the abyss, shared exactly by both sectors. The line
    remains two-sided and nonblocking, and both Brogue cell centers remain
    untouched; only the square floor silhouette is softened.
    """
    neighbor_position = None
    if neighbor is not None:
        neighbor_position = (int(neighbor["x"]), int(neighbor["y"]))
    is_portal = neighbor_position in geometry_cells if neighbor_position is not None else False
    if is_portal and is_chasm_portal(cell, neighbor, cells):
        assert neighbor is not None
        if not cell_is_chasm_void(cell):
            return contoured_side_points(
                height,
                x,
                y,
                side_index,
                contoured=True,
                depth=CHASM_PORTAL_DEPTH,
                shoulder=CHASM_PORTAL_SHOULDER,
            )
        opposite_side = (side_index + 2) % 4
        points = contoured_side_points(
            height,
            int(neighbor["x"]),
            int(neighbor["y"]),
            opposite_side,
            contoured=True,
            depth=CHASM_PORTAL_DEPTH,
            shoulder=CHASM_PORTAL_SHOULDER,
        )
        return list(reversed(points))
    return contoured_side_points(
        height,
        x,
        y,
        side_index,
        contoured=not is_portal and boundary_uses_contour(geometry_cells, x, y, side_index),
    )


def side_texture_offset(x: int, y: int, side_index: int) -> int:
    """Return a world-anchored offset at the clockwise side's first point."""
    if side_index == 0:  # east
        return x * CELL_SIZE
    if side_index == 1:  # south
        return y * CELL_SIZE
    if side_index == 2:  # west
        return -(x + 1) * CELL_SIZE
    return -(y + 1) * CELL_SIZE  # north


def edge_texture_offset(width: int, a: int, b: int) -> int:
    """Anchor wall texture X to the shared world grid.

    Every physical wall is split into 64-unit linedefs. Offset zero on every
    sidedef restarts a larger texture at each Brogue cell and exposes a seam.
    Horizontal lines advance by world X; vertical lines advance in the common
    top-to-bottom linedef direction by Brogue grid Y.
    """
    stride = width + 1
    ax, ay = a % stride, a // stride
    bx, by = b % stride, b // stride
    if ay == by:
        return min(ax, bx) * CELL_SIZE
    return min(ay, by) * CELL_SIZE


def layer_symbol(cell: dict[str, Any], layer: str) -> str:
    return str(cell["layers"][layer]["symbol"])


def render_spec(cell: dict[str, Any], layer: str) -> dict[str, Any]:
    symbol = layer_symbol(cell, layer)
    spec = TERRAIN_RENDER_MAP.get(symbol)
    if spec is None:
        raise CompileError(f"terrain symbol has no render mapping: {symbol}")
    return spec


def cell_is_solid(cell: dict[str, Any]) -> bool:
    semantic = cell.get("semantic")
    if isinstance(semantic, dict) and isinstance(semantic.get("isSolid"), bool):
        return semantic["isSolid"]
    flags = int_field(cell.get("terrainFlags"), "cell.terrainFlags")
    dungeon = layer_symbol(cell, "dungeon")
    return (
        dungeon in DOOR_SYMBOLS
        or bool(render_spec(cell, "dungeon").get("solid", False))
        or bool(flags & PASSABILITY_BLOCKER)
    )


def cell_has_door_geometry(cell: dict[str, Any]) -> bool:
    """Keep Brogue doors as real sectors even while their terrain is solid."""
    return layer_symbol(cell, "dungeon") in DOOR_GEOMETRY_SYMBOLS


def cell_door_is_closed(cell: dict[str, Any]) -> bool:
    """Use Brogue's terrain state, not passability, for visual door closure."""
    return layer_symbol(cell, "dungeon") in DOOR_CLOSED_SYMBOLS


def cell_has_geometry(cell: dict[str, Any]) -> bool:
    return not cell_is_solid(cell) or cell_has_door_geometry(cell)


def cell_is_chasm_void(cell: dict[str, Any]) -> bool:
    """Return true only for the falling part of Brogue chasm terrain.

    Brogue's broader isChasm semantic also covers safe brink/edge tiles. The
    authoritative T_AUTO_DESCENT flag distinguishes the actual hole without
    guessing from a tile ID, while a bridge surface suppresses the void.
    """
    semantic = cell.get("semantic")
    is_chasm = isinstance(semantic, dict) and bool(semantic.get("isChasm"))
    if not is_chasm:
        is_chasm = layer_symbol(cell, "liquid") in {
            "CHASM", "CHASM_WITH_HIDDEN_BRIDGE", "HOLE", "HOLE_GLOW"
        }
    has_bridge = layer_symbol(cell, "surface") in {
        "BRIDGE", "BRIDGE_FALLING", "BRIDGE_EDGE", "STONE_BRIDGE"
    }
    return is_chasm and not has_bridge and bool(int_field(cell.get("terrainFlags"), "cell.terrainFlags") & AUTO_DESCENT)


def cell_is_chasm_bridge(
    cell: dict[str, Any],
    cells: dict[tuple[int, int], dict[str, Any]],
) -> bool:
    """Identify a Brogue bridge whose cardinal surroundings are a chasm."""
    semantic = cell.get("semantic")
    is_bridge = isinstance(semantic, dict) and bool(semantic.get("isBridge"))
    is_chasm = isinstance(semantic, dict) and bool(semantic.get("isChasm"))
    if not is_bridge:
        is_bridge = (
            layer_symbol(cell, "dungeon") == "BRIDGE"
            or layer_symbol(cell, "surface") in {
                "BRIDGE", "BRIDGE_FALLING", "BRIDGE_EDGE", "STONE_BRIDGE"
            }
        )
    return is_bridge and (
        is_chasm
        or any(cell_is_chasm_void(neighbor) for neighbor in adjacent_cells(cell, cells))
    )


def door_sector_tag(x: int, y: int) -> int:
    """Stable tag consumed by the native Brogue-to-GZDoom presentation bridge."""
    return 10000 + y * EXPECTED_WIDTH + x


def floor_layer(cell: dict[str, Any]) -> str:
    """Choose the layer that supplies the visible floor and height.

    Liquids are the primary floor effect. A bridge is the one surface that
    must replace a liquid/chasm underneath it; other surfaces are visual
    overlays and only replace ordinary dungeon floor. Gas remains metadata
    until the turn-based presentation layer is added.
    """
    liquid = layer_symbol(cell, "liquid")
    surface = layer_symbol(cell, "surface")
    if surface in {"BRIDGE", "BRIDGE_FALLING", "BRIDGE_EDGE", "STONE_BRIDGE"}:
        return "surface"
    if liquid != "NOTHING":
        return "liquid"
    if surface != "NOTHING":
        return "surface"
    return "dungeon"


def stable_region_variant_index(seed: Any, depth: int, region_token: str, theme: str, space_kind: str, role: str, count: int) -> int:
    """Choose one stable material variant for a coherent Brogue-space region."""
    value = 14695981039346656037
    fields = (str(seed), str(depth), region_token, theme, space_kind, role)
    for field in fields:
        for byte in (field + "\0").encode("utf-8"):
            value ^= byte
            value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return value % count


def layer_matches(cell: dict[str, Any], layer: str, symbols: list[str]) -> bool:
    return layer_symbol(cell, layer) in symbols


def adjacent_cells(cell: dict[str, Any], cells: dict[tuple[int, int], dict[str, Any]]) -> list[dict[str, Any]]:
    x, y = int(cell["x"]), int(cell["y"])
    return [neighbor for position in ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)) if (neighbor := cells.get(position)) is not None]


def terrain_theme(
    cell: dict[str, Any],
    cells: dict[tuple[int, int], dict[str, Any]] | None = None,
    include_surface: bool = True,
    include_liquid: bool = True,
    include_adjacency: bool = True,
) -> str:
    """Classify visual context while leaving Brogue semantics untouched."""
    if include_liquid and cell_is_chasm_void(cell):
        return "CHASM"
    semantic = cell.get("semantic")
    if include_surface and isinstance(semantic, dict) and semantic.get("isBridge"):
        return "BRIDGE"
    for rule in TERRAIN_THEME_REGISTRY.get("rules", []):
        if not include_surface and rule.get("layer") == "surface":
            continue
        if not include_liquid and rule.get("layer") == "liquid":
            continue
        if layer_matches(cell, str(rule["layer"]), list(rule.get("symbols", []))):
            return str(rule["theme"])

    # Machine-numbered regions are the strongest room/special-structure hint
    # currently exported by Brogue. Specific liquid/crystal/surface rules above
    # retain priority over this presentation-only classification.
    if int(cell.get("machine", 0)) != 0:
        return "RUINS_WORKED_STONE"

    if include_adjacency and cells is not None:
        for rule in TERRAIN_THEME_REGISTRY.get("adjacencyRules", []):
            neighbor_layer = str(rule["neighborLayer"])
            neighbor_symbols = list(rule.get("neighborSymbols", []))
            if any(layer_matches(neighbor, neighbor_layer, neighbor_symbols) for neighbor in adjacent_cells(cell, cells)):
                return str(rule["theme"])

    return str(TERRAIN_THEME_REGISTRY["defaultTheme"])


def surface_tint(cell: dict[str, Any]) -> int:
    """Return a subtle presentation tint without replacing Brogue's base floor layer."""
    surface = layer_symbol(cell, "surface")
    tint = TERRAIN_THEME_REGISTRY["surfaceTints"].get(surface)
    return 0xFFFFFF if tint is None else int(tint)


def material_neighbors(position: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    x, y = position
    return ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y))


def material_space_kind(position: tuple[int, int], cell: dict[str, Any], geometry_positions: set[tuple[int, int]]) -> str:
    """Classify presentation space from Brogue topology, not from texture IDs.

    Brogue's current neutral snapshot does not expose room IDs. A compact
    topology classifier still lets the renderer keep broad room regions and
    narrow corridors visually coherent while preserving the raw Brogue state.
    """
    semantic = cell.get("semantic")
    if isinstance(semantic, dict):
        if semantic.get("isDoor"):
            return "DOORWAY"
        if semantic.get("isChasm"):
            return "CHASM"

    cardinal_degree = sum(neighbor in geometry_positions for neighbor in material_neighbors(position))
    local_density = sum(
        (position[0] + dx, position[1] + dy) in geometry_positions
        for dy in (-1, 0, 1)
        for dx in (-1, 0, 1)
    )
    diagonal_density = sum(
        (position[0] + dx, position[1] + dy) in geometry_positions
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    )

    # Room corners often have only two cardinal neighbors, so include the
    # local 3x3 shape when deciding whether a cell belongs to a room. Brogue's
    # diagonal-opening cleanup makes one-cell corridor bends much sparser.
    if cardinal_degree >= 3 or local_density >= 6 or diagonal_density >= 1:
        return "ROOM"
    return "CORRIDOR"


def build_material_layout(
    cells: dict[tuple[int, int], dict[str, Any]],
    geometry_cells: dict[tuple[int, int], dict[str, Any]],
) -> dict[str, Any]:
    """Build stable region/topology metadata for one generated Brogue level."""
    geometry_positions = set(geometry_cells)
    theme_by_position = {
        # Ordinary surface terrain is represented by color_floor below, while
        # the BRIDGE rule remains an explicit deck replacing liquid/chasm.
        position: terrain_theme(cell, cells)
        for position, cell in geometry_cells.items()
    }
    wall_theme_by_position = {
        position: terrain_theme(cell, cells, include_surface=False, include_liquid=False)
        for position, cell in geometry_cells.items()
    }
    # Depth 1 needs one visually continuous cave roof. A black CHASM flat over
    # only some cells is still a real horizontal polygon; when viewed obliquely
    # its moving projection looks like a tall rectangular wall. Lower depths
    # replace this material with one F_SKY1 void in sector_text().
    ceiling_theme_by_position = {
        position: TERRAIN_THEME_REGISTRY["defaultTheme"]
        for position in geometry_cells
    }
    space_by_position = {
        position: material_space_kind(position, cell, geometry_positions)
        for position, cell in geometry_cells.items()
    }

    def connected_regions(
        themes: dict[tuple[int, int], str],
    ) -> tuple[dict[tuple[int, int], int], dict[int, dict[str, Any]]]:
        region_by_position: dict[tuple[int, int], int] = {}
        regions: dict[int, dict[str, Any]] = {}
        next_region = 0
        for origin in sorted(geometry_positions):
            if origin in region_by_position:
                continue
            region_key = (themes[origin], space_by_position[origin])
            queue = [origin]
            region_by_position[origin] = next_region
            region_cells: list[tuple[int, int]] = []
            while queue:
                position = queue.pop(0)
                region_cells.append(position)
                for neighbor in material_neighbors(position):
                    if neighbor not in geometry_positions or neighbor in region_by_position:
                        continue
                    if (themes[neighbor], space_by_position[neighbor]) != region_key:
                        continue
                    region_by_position[neighbor] = next_region
                    queue.append(neighbor)
            regions[next_region] = {
                "theme": region_key[0],
                "space": region_key[1],
                "cells": tuple(region_cells),
            }
            next_region += 1
        return region_by_position, regions

    region_by_position, regions = connected_regions(theme_by_position)
    wall_region_by_position, wall_regions = connected_regions(wall_theme_by_position)
    ceiling_region_by_position, ceiling_regions = connected_regions(ceiling_theme_by_position)

    return {
        "theme_by_position": theme_by_position,
        "wall_theme_by_position": wall_theme_by_position,
        "ceiling_theme_by_position": ceiling_theme_by_position,
        "space_by_position": space_by_position,
        "region_by_position": region_by_position,
        "wall_region_by_position": wall_region_by_position,
        "ceiling_region_by_position": ceiling_region_by_position,
        "regions": regions,
        "wall_regions": wall_regions,
        "ceiling_regions": ceiling_regions,
    }


def ensure_material_layout(
    cells: dict[tuple[int, int], dict[str, Any]],
    layout: dict[str, Any] | None,
) -> dict[str, Any]:
    if layout is not None:
        return layout
    geometry_cells = {
        position: cell
        for position, cell in cells.items()
        if not cell_is_solid(cell)
    }
    return build_material_layout(cells, geometry_cells)


def material_variant_token(position: tuple[int, int], layout: dict[str, Any], role: str) -> str:
    """Use one coherent material palette per level, theme, and space kind."""
    del position, layout, role
    return "level-palette"


def role_theme_map(role: str) -> str:
    if role == "walls":
        return "wall_theme_by_position"
    if role == "ceilings":
        return "ceiling_theme_by_position"
    return "theme_by_position"


def theme_asset(
    cell: dict[str, Any],
    cells: dict[tuple[int, int], dict[str, Any]],
    seed: Any,
    depth: int,
    role: str,
    theme: str | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    position = (int(cell["x"]), int(cell["y"]))
    layout = ensure_material_layout(cells, layout)
    if theme is None:
        theme_map_name = role_theme_map(role)
        selected_theme = str(layout[theme_map_name].get(position, terrain_theme(cell, cells, include_surface=False)))
    else:
        selected_theme = theme
    # Project Broom palettes are deliberately curated per semantic role. Keeping
    # the first entry authoritative prevents a per-cell checkerboard effect.
    del seed, depth
    assets = TERRAIN_THEME_REGISTRY["themes"][selected_theme][role]
    return str(assets[0])


def door_asset(
    cell: dict[str, Any],
    cells: dict[tuple[int, int], dict[str, Any]],
    seed: Any,
    depth: int,
    layout: dict[str, Any] | None = None,
) -> str:
    layout = ensure_material_layout(cells, layout)
    position = (int(cell["x"]), int(cell["y"]))
    theme = str(layout["wall_theme_by_position"].get(position, terrain_theme(cell, cells, include_surface=False)))
    return str(TERRAIN_THEME_REGISTRY["themes"][theme]["door"])


def floor_material(
    cell: dict[str, Any],
    seed: Any = "0",
    depth: int = 0,
    cells: dict[tuple[int, int], dict[str, Any]] | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    cells = cells or {(int(cell["x"]), int(cell["y"])): cell}
    if floor_layer(cell) == "surface" and layer_symbol(cell, "surface") in VEGETATED_FLOOR_SURFACES:
        return "BRGMOSS"
    return theme_asset(cell, cells, seed, depth, "floors", layout=layout)


def wall_material(
    cell: dict[str, Any],
    seed: Any = "0",
    depth: int = 0,
    cells: dict[tuple[int, int], dict[str, Any]] | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    cells = cells or {(int(cell["x"]), int(cell["y"])): cell}
    # Door panels are actors, not wall skins. A door cell can border solid
    # rock on its lateral sides; painting those boundaries with the door image
    # made whole wall columns look like permanently closed doors.
    return theme_asset(cell, cells, seed, depth, "walls", layout=layout)


def boundary_material(
    front_cell: dict[str, Any],
    back_cell: dict[str, Any] | None,
    seed: Any = "0",
    depth: int = 0,
    cells: dict[tuple[int, int], dict[str, Any]] | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    cells = cells or {(int(front_cell["x"]), int(front_cell["y"])): front_cell}
    return wall_material(front_cell, seed, depth, cells, layout)


def transition_material(
    front_cell: dict[str, Any],
    back_cell: dict[str, Any],
    seed: Any,
    depth: int,
    cells: dict[tuple[int, int], dict[str, Any]],
    layout: dict[str, Any],
) -> str:
    lower_cell = front_cell if floor_height(front_cell) < floor_height(back_cell) else back_cell
    lower_position = (int(lower_cell["x"]), int(lower_cell["y"]))
    theme = str(layout["theme_by_position"].get(lower_position, terrain_theme(lower_cell, cells)))
    fall = TERRAIN_THEME_REGISTRY["themes"][theme].get("fall")
    if fall and floor_height(front_cell) != floor_height(back_cell):
        return str(fall)
    return wall_material(front_cell, seed, depth, cells, layout)


def floor_height(cell: dict[str, Any]) -> int:
    surface = layer_symbol(cell, "surface")
    liquid = layer_symbol(cell, "liquid")
    if surface in {"BRIDGE", "BRIDGE_FALLING", "BRIDGE_EDGE", "STONE_BRIDGE"}:
        return 0
    if cell_is_chasm_void(cell):
        return CHASM_FLOOR_Z
    semantic = cell.get("semantic")
    if isinstance(semantic, dict) and semantic.get("isChasm"):
        # CHASM_EDGE, HOLE_EDGE and machine brink tiles describe safe ground
        # beside the void. Their legacy render-map value was inherited from
        # the old shallow-pit presentation and must not lower the brink.
        return 0
    if liquid in {"DEEP_WATER", "FLOOD_WATER_DEEP", "DEEP_WATER_ALGAE_WELL", "DEEP_WATER_ALGAE_1", "DEEP_WATER_ALGAE_2"}:
        return -24
    if liquid in {"SHALLOW_WATER", "FLOOD_WATER_SHALLOW"}:
        return -8
    if liquid in {"LAVA", "LAVA_RETRACTABLE", "LAVA_RETRACTING", "ACTIVE_BRIMSTONE", "INERT_BRIMSTONE", "SACRIFICE_LAVA"}:
        return -12
    if liquid == "MUD" or layer_symbol(cell, "dungeon") == "MUD_FLOOR":
        return -4
    return int(render_spec(cell, floor_layer(cell)).get("floorHeight", 0))


def prop_placement(cell: dict[str, Any], game_seed: Any, depth: int, width: int, height: int) -> dict[str, Any] | None:
    """Return one deterministic, presentation-only prop for a Brogue cell."""
    surface = layer_symbol(cell, "surface")
    rule = PROP_RULES.get(surface)
    if rule is None:
        return None
    role, thing_type, denominator = rule
    x = int_field(cell["x"], "cell.x")
    y = int_field(cell["y"], "cell.y")
    digest = hashlib.sha256(f"prop:{game_seed}:{depth}:{x}:{y}:{surface}".encode("ascii")).digest()
    if digest[0] % denominator:
        return None
    center_x, center_y = cell_center(width, height, x, y)
    return {
        "role": role,
        "surface": surface,
        "type": thing_type,
        "x": center_x + (digest[1] % 25) - 12,
        "y": center_y + (digest[2] % 25) - 12,
        "z": floor_height(cell),
        "angle": (digest[3] % 8) * 45,
    }


def sector_ceiling(
    cell: dict[str, Any],
    position: tuple[int, int],
    layout: dict[str, Any],
    depth: int = 1,
) -> int:
    # All sectors share one logical ceiling height. Brogue's dense cell grid
    # cannot safely mix room/corridor/chasm heights: every mismatch requires an
    # upper sidedef, which reads as a freestanding rectangular wall around
    # bridges and pits. Depth 1 still chooses semantic rock/abyss materials;
    # lower depths use F_SKY1 for an open black void.
    del cell, position, layout, depth
    return OPEN_VOID_CEILING_Z


def sector_light(
    cell: dict[str, Any],
    position: tuple[int, int],
    depth: int,
    cells: dict[tuple[int, int], dict[str, Any]],
    layout: dict[str, Any],
) -> int:
    theme = str(layout["theme_by_position"].get(position, TERRAIN_THEME_REGISTRY["defaultTheme"]))
    base = 144 - min(32, max(0, depth - 1))
    # Every Brogue cell is an independently addressable Doom sector. Applying
    # room/corridor light per cell creates hard 64-unit bands wherever the
    # topology classifier changes. Keep ordinary cave light continuous and
    # reserve sector-level changes for meaningful terrain below.
    if int(cell.get("machine", 0)):
        return max(base, 160)
    if theme == "LAVA":
        return 192
    if theme == "CHASM":
        # BRGABYSS and BRGVOID provide the darkness. Keeping the sector itself
        # at the minimum cave light prevents its structural perimeter walls
        # from becoming featureless floor-to-ceiling silhouettes.
        return CHASM_LIGHT_LEVEL
    if theme == "WATER":
        return max(base, 128)
    if any(terrain_theme(neighbor, cells) == "LAVA" for neighbor in adjacent_cells(cell, cells)):
        return max(base, 168)
    return max(112, base)


def sector_tint(cell: dict[str, Any], theme: str) -> int:
    themed = {
        "WATER": 0xA8C8E8,
        "SLUDGE": 0x8FA06A,
        "LAVA": 0xFF9A50,
        "CHASM": 0x303040,
    }
    # Surface-layer colors are retained in UDMF metadata for later actors or
    # decals. Applying them to color_floor tints an entire 64x64 sector and
    # exposes the Brogue grid as dark rectangular bands.
    return themed.get(theme, 0xFFFFFF)


def make_sector_text(
    cell: dict[str, Any],
    width: int,
    depth: int,
    sector_index: int,
    game_seed: Any = "0",
    cells: dict[tuple[int, int], dict[str, Any]] | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    del width
    # Keep every UDMF sector non-degenerate. Solidity is enforced by the
    # one-sided grid walls, while a zero-height sector makes GZDoom's runtime
    # node builder explode on the complete 79x29 lattice before the map can
    # render. The Brogue solid/passability state remains authoritative in the
    # per-sector metadata and in the wall topology.
    cells = cells or {(int(cell["x"]), int(cell["y"])): cell}
    layout = ensure_material_layout(cells, layout)
    position = (int(cell["x"]), int(cell["y"]))
    theme = str(layout["theme_by_position"].get(position, terrain_theme(cell, cells)))
    wall_theme = str(
        layout["wall_theme_by_position"].get(
            position,
            terrain_theme(cell, cells, include_surface=False, include_liquid=False),
        )
    )
    ceiling_theme = str(layout["ceiling_theme_by_position"].get(position, TERRAIN_THEME_REGISTRY["defaultTheme"]))
    region_id = int(layout["region_by_position"].get(position, 0))
    space_kind = str(layout["space_by_position"].get(position, "CELL"))
    ceiling = sector_ceiling(cell, position, layout, depth)
    floor = floor_material(cell, game_seed, depth, cells, layout)
    ceiling_material = (
        OPEN_VOID_SKY_FLAT
        if depth > 1
        else theme_asset(cell, cells, game_seed, depth, "ceilings", ceiling_theme, layout)
    )
    floor_tint = sector_tint(cell, theme)
    metadata_surface_tint = surface_tint(cell)
    light = sector_light(cell, position, depth, cells, layout)
    sector_tag = door_sector_tag(position[0], position[1]) if cell_has_door_geometry(cell) else sector_index
    return "".join(
        [
            "sector {\n",
            f"  heightfloor = {floor_height(cell)};\n",
            f"  heightceiling = {ceiling};\n",
            f"  texturefloor = {text(floor)};\n",
            f"  textureceiling = {text(ceiling_material)};\n",
            f"  color_floor = {floor_tint};\n",
            f"  lightlevel = {light};\n",
            "  special = 0;\n",
            f"  id = {sector_tag};\n",
            f"  user_brogue_x = {int_field(cell['x'], 'cell.x')};\n",
            f"  user_brogue_y = {int_field(cell['y'], 'cell.y')};\n",
            f"  user_brogue_depth = {depth};\n",
            f"  user_brogue_dungeon = {int_field(cell['layers']['dungeon']['id'], 'dungeon.id')};\n",
            f"  user_brogue_liquid = {int_field(cell['layers']['liquid']['id'], 'liquid.id')};\n",
            f"  user_brogue_gas = {int_field(cell['layers']['gas']['id'], 'gas.id')};\n",
            f"  user_brogue_surface = {int_field(cell['layers']['surface']['id'], 'surface.id')};\n",
            f"  user_brogue_cell_flags = {int_field(cell['flags'], 'cell.flags')};\n",
            f"  user_brogue_terrain_flags = {int_field(cell['terrainFlags'], 'cell.terrainFlags')};\n",
            f"  user_brogue_tm_flags = {int_field(cell['terrainMechFlags'], 'cell.terrainMechFlags')};\n",
            f"  user_brogue_machine = {int_field(cell['machine'], 'cell.machine')};\n",
            f"  user_brogue_volume = {int_field(cell['volume'], 'cell.volume')};\n",
            f"  user_brogue_theme = {text(theme)};\n",
            f"  user_brogue_wall_theme = {text(wall_theme)};\n",
            f"  user_brogue_ceiling_theme = {text(ceiling_theme)};\n",
            f"  user_brogue_surface_tint = {metadata_surface_tint};\n",
            f"  user_brogue_region = {region_id};\n",
            f"  user_brogue_space = {text(space_kind)};\n",
            f"  user_brogue_door_sector = {1 if cell_has_door_geometry(cell) else 0};\n",
            "}\n",
        ]
    )


def make_map_text(level: dict[str, Any], width: int, height: int, map_name: str | None = None, game_seed: Any = "") -> tuple[str, str, dict[str, Any]]:
    depth = int_field(level["depth"], "level.depth")
    map_name = map_name or f"BRG{depth:02d}"
    game_seed = str(game_seed)
    cells = {(int(cell["x"]), int(cell["y"])): cell for cell in level["cells"]}
    # Traversable cells and dynamic door cells receive physical sectors.
    # Other solid cells remain one-sided perimeter walls. Door sectors remain
    # open, valid volumes; Brogue-controlled marker models show closed panels.
    geometry_cells = {position: cell for position, cell in cells.items() if cell_has_geometry(cell)}
    material_layout = build_material_layout(cells, geometry_cells)
    sorted_geometry_positions = sorted(geometry_cells)
    geometry_indices = {position: index for index, position in enumerate(sorted_geometry_positions)}
    geometry_positions_by_index = {index: position for position, index in geometry_indices.items()}
    lines: list[dict[str, Any]] = []
    vertices: list[tuple[int, int]] = []
    vertex_indices: dict[tuple[int, int], int] = {}
    edges: dict[tuple[int, int], dict[str, Any]] = {}
    sidedefs: list[dict[str, Any]] = []
    boundary_count = 0
    contoured_boundary_count = 0
    chasm_portal_count = 0

    def vertex_index(position: tuple[int, int]) -> int:
        if position not in vertex_indices:
            vertex_indices[position] = len(vertices)
            vertices.append(position)
        return vertex_indices[position]

    def add_edge(
        start: tuple[int, int],
        end: tuple[int, int],
        cell: dict[str, Any],
        neighbor: dict[str, Any] | None,
        texture_offset: int,
    ) -> None:
        a = vertex_index(start)
        b = vertex_index(end)
        key = (min(a, b), max(a, b))
        if key not in edges:
            edges[key] = {
                "a": a,
                "b": b,
                "front": geometry_indices[(int(cell["x"]), int(cell["y"]))],
                "front_position": (int(cell["x"]), int(cell["y"])),
                "back": None,
                "boundary": neighbor,
                "offsetx": texture_offset,
            }
        elif edges[key]["back"] is None:
            edges[key]["back"] = geometry_indices[(int(cell["x"]), int(cell["y"]))]

    for y in range(height):
        for x in range(width):
            if (x, y) not in geometry_cells:
                continue
            cell = cells[(x, y)]
            neighbors = [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]
            for side_index, neighbor_pos in enumerate(neighbors):
                is_portal = neighbor_pos in geometry_cells
                use_contour = not is_portal and boundary_uses_contour(geometry_cells, x, y, side_index)
                use_chasm_portal = is_portal and is_chasm_portal(cell, cells.get(neighbor_pos), cells)
                if not is_portal:
                    boundary_count += 1
                    contoured_boundary_count += int(use_contour)
                elif use_chasm_portal and (x, y) < neighbor_pos:
                    chasm_portal_count += 1
                points = map_side_points(
                    height,
                    x,
                    y,
                    side_index,
                    cell,
                    cells.get(neighbor_pos),
                    cells,
                    geometry_cells,
                )
                running_offset = side_texture_offset(x, y, side_index)
                for start, end in zip(points, points[1:]):
                    add_edge(start, end, cell, cells.get(neighbor_pos), running_offset)
                    running_offset += round(math.hypot(end[0] - start[0], end[1] - start[1]))

    edge_items = sorted(edges.items(), key=lambda item: item[0])
    edge_to_line: dict[tuple[int, int], int] = {}
    for line_index, (edge_key, edge) in enumerate(edge_items):
        edge_to_line[edge_key] = line_index
        back = edge["back"]
        front_cell = cells[edge["front_position"]]
        line_v1 = edge["a"]
        line_v2 = edge["b"]
        boundary_cell = edge["boundary"]
        back_cell = cells[geometry_positions_by_index[back]] if back is not None else None
        is_door_boundary = (
            (boundary_cell is not None and cell_has_door_geometry(boundary_cell))
            or cell_has_door_geometry(front_cell)
            or (back_cell is not None and cell_has_door_geometry(back_cell))
        )
        # BRGDOOR is a single framed panel sized to one Brogue boundary. It
        # must begin at its own origin instead of continuing the cave wall's
        # world-space panning across the door.
        texture_offset = 0 if is_door_boundary else edge["offsetx"]
        if back is None:
            blocked = True
            front_side = len(sidedefs)
            sidedefs.append({"sector": edge["front"], "offsetx": texture_offset, "texturemiddle": boundary_material(front_cell, edge["boundary"], game_seed, depth, cells, material_layout), "texturetop": "-", "texturebottom": "-"})
            back_side = None
        else:
            blocked = False
            back_position = geometry_positions_by_index[back]
            assert back_cell is not None
            front_floor = floor_height(front_cell)
            back_floor = floor_height(back_cell)
            front_ceiling = sector_ceiling(front_cell, edge["front_position"], material_layout, depth)
            back_ceiling = sector_ceiling(back_cell, back_position, material_layout, depth)
            lower_texture = (
                transition_material(front_cell, back_cell, game_seed, depth, cells, material_layout)
                if front_floor != back_floor
                else "-"
            )
            if front_ceiling != back_ceiling:
                # Height transitions above doorways are cave structure. The
                # dedicated marker model is the only rendered door panel.
                upper_texture = wall_material(front_cell, game_seed, depth, cells, material_layout)
            else:
                upper_texture = "-"
            front_side = len(sidedefs)
            sidedefs.append({"sector": edge["front"], "offsetx": texture_offset, "texturemiddle": "-", "texturetop": upper_texture, "texturebottom": lower_texture})
            back_side = len(sidedefs)
            sidedefs.append({"sector": back, "offsetx": texture_offset, "texturemiddle": "-", "texturetop": upper_texture, "texturebottom": lower_texture})
            two_sided = True
        if back is None:
            two_sided = False
        lines.append({"v1": line_v1, "v2": line_v2, "front": front_side, "back": back_side, "two_sided": two_sided, "blocking": blocked, "door_portal": is_door_boundary and back is not None})

    parts = ['namespace = "ZDoom";\n']
    for vertex_x, vertex_y in vertices:
        parts.append(f"vertex {{ x = {vertex_x}; y = {vertex_y}; }}\n")

    for line in lines:
        parts.append("linedef {\n")
        parts.append(f"  v1 = {line['v1']}; v2 = {line['v2']};\n")
        parts.append(f"  sidefront = {line['front']};\n")
        if line["back"] is not None:
            parts.append(f"  sideback = {line['back']}; twosided = {'true' if line['two_sided'] else 'false'};\n")
        else:
            parts.append("  twosided = false;\n")
        parts.append(f"  blocking = {'true' if line['blocking'] else 'false'};\n")
        parts.append(f"  blockplayers = {'true' if line['blocking'] else 'false'};\n")
        if not line["blocking"] and not line["door_portal"]:
            # Open cell-to-cell portals are required for sector topology but
            # are not meaningful cave boundaries. Hiding them keeps both the
            # native automap and UltimateClassicMinimap from drawing thousands
            # of internal grid lines every frame.
            parts.append("  dontdraw = true;\n")
        parts.append("}\n")

    for side in sidedefs:
        parts.append("sidedef {\n")
        parts.append(f"  offsetx = {side['offsetx']}; offsety = 0;\n")
        parts.append(f"  texturemiddle = {text(side['texturemiddle'])};\n")
        # UDMF names these tiers top and bottom. `textureupper`/`texturelower`
        # are not aliases: GZDoom ignores them as unknown custom keys, leaving
        # height transitions untextured and exposing renderer plane-bleed
        # fallbacks instead of the intended cliff, bank, or structural wall.
        parts.append(f"  texturetop = {text(side['texturetop'])};\n")
        parts.append(f"  texturebottom = {text(side['texturebottom'])};\n")
        parts.append(f"  sector = {side['sector']};\n")
        parts.append("}\n")

    for sector_index, position in enumerate(sorted_geometry_positions):
        parts.append(make_sector_text(geometry_cells[position], width, depth, sector_index, game_seed, cells, material_layout))

    up_x = int_field(level["upStairs"]["x"], "upStairs.x")
    up_y = int_field(level["upStairs"]["y"], "upStairs.y")
    down_x = int_field(level["downStairs"]["x"], "downStairs.x")
    down_y = int_field(level["downStairs"]["y"], "downStairs.y")
    up_world = cell_center(width, height, up_x, up_y)
    down_world = cell_center(width, height, down_x, down_y)

    def start_angle(x: int, y: int) -> int:
        # Face into the generated dungeon instead of arbitrarily into the
        # nearest wall. Doom angles are east=0, north=90, west=180, south=270
        # after the explicit Brogue-Y inversion above.
        for (dx, dy), angle in (((1, 0), 0), ((0, -1), 90), ((-1, 0), 180), ((0, 1), 270)):
            neighbor = cells.get((x + dx, y + dy))
            if neighbor is not None and not cell_is_solid(neighbor):
                return angle
        return 0

    def thing(
        x: int,
        y: int,
        thing_type: int,
        angle: int = 0,
        z: int = 0,
        scale_y: float | None = None,
        args: tuple[int, ...] = (),
        alpha: float | None = None,
    ) -> str:
        scale_text = "" if scale_y is None else f"  scaley = {scale_y:.6f};\n"
        args_text = "".join(f"  arg{index} = {value};\n" for index, value in enumerate(args))
        alpha_text = "" if alpha is None else f"  alpha = {alpha:.6f};\n"
        return "".join(
            [
                "thing {\n",
                f"  x = {x}; y = {y}; z = {z}; angle = {angle}; type = {thing_type};\n",
                scale_text,
                args_text,
                alpha_text,
                "  skill1 = true; skill2 = true; skill3 = true; skill4 = true; skill5 = true;\n",
                "  single = true; coop = true; dm = true;\n",
                "}\n",
            ]
        )

    def stair_marker_position(world: tuple[int, int], angle: int) -> tuple[int, int]:
        # Ladder and pit models are authored around the actor origin. The
        # visual and logical actors therefore share the exact Brogue cell
        # center; angle points their open approach toward a traversable cell.
        return world

    up_angle = start_angle(up_x, up_y)
    down_angle = start_angle(down_x, down_y)
    up_marker_world = stair_marker_position(up_world, up_angle)
    down_marker_world = stair_marker_position(down_world, down_angle)
    parts.append(thing(*up_world, 1, up_angle))
    parts.append(thing(*up_world, 15000))
    up_cell = geometry_cells[(up_x, up_y)]
    up_ladder_height = sector_ceiling(up_cell, (up_x, up_y), material_layout, depth) - floor_height(up_cell)
    parts.append(thing(*up_marker_world, 15002, up_angle, floor_height(up_cell), up_ladder_height / 128.0))
    if (up_x, up_y) != (down_x, down_y):
        parts.append(thing(*down_world, 15001))
    else:
        parts.append(thing(*down_world, 15001))
    parts.append(thing(*down_marker_world, 15003, down_angle))

    # Every dynamic Brogue door receives one stable presentation actor. The
    # native bridge toggles this actor from authoritative terrain state; open
    # doors begin hidden even in a generated map inspected without the bridge.
    for door_x, door_y in sorted(position for position in geometry_cells if cell_has_door_geometry(geometry_cells[position])):
        door_cell = geometry_cells[(door_x, door_y)]
        door_world = cell_center(width, height, door_x, door_y)
        closed = cell_door_is_closed(door_cell)
        marker_type = 15021 if layer_symbol(door_cell, "dungeon") == "WOODEN_BARRICADE" else 15020
        parts.append(
            thing(
                *door_world,
                marker_type,
                start_angle(door_x, door_y),
                floor_height(door_cell),
                args=(door_x, door_y),
                alpha=1.0 if closed else 0.0,
            )
        )

    stair_positions = {(up_x, up_y), (down_x, down_y)}
    props: list[dict[str, Any]] = []
    for position in sorted_geometry_positions:
        if position in stair_positions:
            continue
        placement = prop_placement(geometry_cells[position], game_seed, depth, width, height)
        if placement is None:
            continue
        props.append(placement)
        parts.append(
            thing(
                int(placement["x"]),
                int(placement["y"]),
                int(placement["type"]),
                int(placement["angle"]),
                int(placement["z"]),
            )
        )
    parts.append("\n")
    map_text = "".join(parts)
    theme_counts: dict[str, int] = {}
    space_counts: dict[str, int] = {}
    prop_counts: dict[str, int] = {}
    for cell in geometry_cells.values():
        position = (int(cell["x"]), int(cell["y"]))
        theme = str(material_layout["theme_by_position"][position])
        space_kind = str(material_layout["space_by_position"][position])
        theme_counts[theme] = theme_counts.get(theme, 0) + 1
        space_counts[space_kind] = space_counts.get(space_kind, 0) + 1
    for prop in props:
        role = str(prop["role"])
        prop_counts[role] = prop_counts.get(role, 0) + 1
    metadata = {
        "name": map_name,
        "depth": depth,
        "levelSeed": str(level["levelSeed"]),
        "upStairs": {"x": up_x, "y": up_y},
        "downStairs": {"x": down_x, "y": down_y},
        "sectorCount": len(geometry_cells),
        "vertexCount": len(vertices),
        "contourDepth": CONTOUR_DEPTH,
        "contourShoulder": CONTOUR_SHOULDER,
        "boundaryCount": boundary_count,
        "contouredBoundaryCount": contoured_boundary_count,
        "chasmPortalCount": chasm_portal_count,
        "propCount": len(props),
        "propCounts": dict(sorted(prop_counts.items())),
        "lineCount": len(lines),
        "sidedefCount": len(sidedefs),
        "themeCounts": dict(sorted(theme_counts.items())),
        "spaceCounts": dict(sorted(space_counts.items())),
        "regionCount": len(material_layout["regions"]),
        "mapSha256": hashlib.sha256(map_text.encode("utf-8")).hexdigest(),
    }
    if metadata["sectorCount"] != len(geometry_cells):
        raise CompileError("internal sector count mismatch")
    if metadata["vertexCount"] != len(vertex_indices):
        raise CompileError("internal vertex count mismatch")
    return map_text, f"{map_name}.wad", metadata


def wad_lump(name: str, data: bytes) -> tuple[str, bytes]:
    return name, data


def make_wad(map_name: str, textmap: str) -> bytes:
    lumps = [
        wad_lump(map_name, b""),
        wad_lump("TEXTMAP", textmap.encode("utf-8")),
        wad_lump("ENDMAP", b""),
    ]
    offset = 12
    payloads: list[bytes] = []
    directory: list[tuple[int, int, str]] = []
    for name, payload in lumps:
        directory.append((offset, len(payload), name))
        payloads.append(payload)
        offset += len(payload)
    directory_offset = offset
    result = bytearray(struct.pack("<4sii", b"PWAD", len(lumps), directory_offset))
    for payload in payloads:
        result.extend(payload)
    for lump_offset, size, name in directory:
        encoded_name = name.encode("ascii")[:8].ljust(8, b"\0")
        result.extend(struct.pack("<ii8s", lump_offset, size, encoded_name))
    return bytes(result)


def make_mapinfo(map_entries: list[tuple[str, int]]) -> str:
    parts = ["cluster 1\n{\n  hub\n}\n\n"]
    for index, (name, depth) in enumerate(map_entries):
        parts.append(f"map {name} \"Project Broom - Depth {depth}\"\n{{\n  levelnum = {depth}\n  cluster = 1\n  nointermission\n")
        if depth > 1:
            parts.append(f"  sky1 = \"{OPEN_VOID_SKY_TEXTURE}\", 0\n")
        if index + 1 < len(map_entries):
            parts.append(f"  next = \"{map_entries[index + 1][0]}\"\n")
        parts.append("}\n\n")
    return "".join(parts)


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 0
    info.external_attr = 0o644 << 16
    return info


def compile_package(input_path: Path, output_path: Path, depth: int | None = None, map_name: str | None = None) -> dict[str, Any]:
    try:
        model = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CompileError(f"could not read JSON input: {error}") from error
    if not isinstance(model, dict):
        raise CompileError("JSON root is not an object")
    width, height, _ = validate_model(model)
    all_levels = model["levels"]
    if depth is None:
        levels = all_levels
        map_names = [f"BRG{int(level['depth']):02d}" for level in levels]
    else:
        if depth < 1 or depth > len(all_levels):
            raise CompileError(f"requested depth {depth} is outside the exported level range")
        if map_name is None:
            map_name = "MAP01"
        if not map_name or len(map_name) > 8 or not map_name.isascii() or not map_name.isalnum():
            raise CompileError("map name must be 1-8 ASCII alphanumeric characters")
        levels = [all_levels[depth - 1]]
        map_names = [map_name.upper()]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    map_files: list[tuple[str, bytes]] = []
    maps_metadata: list[dict[str, Any]] = []
    for level, current_map_name in zip(levels, map_names):
        textmap, wad_name, metadata = make_map_text(level, width, height, current_map_name, model.get("seed", ""))
        wad = make_wad(current_map_name, textmap)
        metadata["wadSha256"] = hashlib.sha256(wad).hexdigest()
        map_files.append((f"maps/{wad_name.lower() if depth is not None else wad_name}", wad))
        maps_metadata.append(metadata)

    manifest: dict[str, Any] = {
        "schemaVersion": 1,
        "compilerVersion": COMPILER_VERSION,
        "inputSha256": sha256_file(input_path),
        "resourcePack": "Project Broom Original Cave Textures",
        "resourceSha256": resource_pack_hash(),
        "materialRegistryVersion": int(TERRAIN_THEME_REGISTRY["schemaVersion"]),
        "referenceAnalysisHash": "not-applicable-original-art",
        "source": model.get("source", {}),
        "seed": str(model.get("seed", "")),
        "dimensions": {"width": width, "height": height, "cellSize": CELL_SIZE},
        "maps": maps_metadata,
    }
    manifest_bytes = canonical_json(manifest)
    mapinfo_bytes = make_mapinfo([(name, int(level["depth"])) for name, level in zip(map_names, levels)]).encode("utf-8")

    entries = sorted(
        map_files + [("MAPINFO", mapinfo_bytes), ("brogue-manifest.json", manifest_bytes)],
        key=lambda item: item[0],
    )
    temporary_output = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        with zipfile.ZipFile(temporary_output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, payload in entries:
                archive.writestr(zip_info(name), payload)
        temporary_output.replace(output_path)
    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise

    manifest_path = output_path.parent / "brogue-manifest.json"
    manifest_path.write_bytes(manifest_bytes)
    return manifest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--depth", type=int, help="compile only one exported depth as a standalone map")
    parser.add_argument("--map-name", default=None, help="map marker for --depth mode; defaults to MAP01")
    args = parser.parse_args(argv)
    try:
        manifest = compile_package(args.input, args.output, args.depth, args.map_name)
    except CompileError as error:
        print(f"mapcompiler: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.output), "maps": len(manifest["maps"]), "inputSha256": manifest["inputSha256"]}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
