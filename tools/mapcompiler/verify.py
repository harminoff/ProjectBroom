#!/usr/bin/env python3
"""Verify that a generated Brogue PK3 round-trips its JSON map contract."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

try:
    from .compile import (
        CAVE_CEILING_Z,
        OPEN_VOID_CEILING_Z,
        OPEN_VOID_SKY_FLAT,
        PROP_RULES,
        cell_center,
        cell_has_door_geometry,
        cell_door_is_closed,
        cell_has_geometry,
        cell_is_solid,
        layer_symbol,
        map_side_points,
        prop_placement,
        validate_model,
        make_mapinfo,
    )
except ImportError:
    from compile import (  # type: ignore[no-redef]
        CAVE_CEILING_Z,
        OPEN_VOID_CEILING_Z,
        OPEN_VOID_SKY_FLAT,
        PROP_RULES,
        cell_center,
        cell_has_door_geometry,
        cell_door_is_closed,
        cell_has_geometry,
        cell_is_solid,
        layer_symbol,
        map_side_points,
        prop_placement,
        validate_model,
        make_mapinfo,
    )


class VerifyError(ValueError):
    pass


BLOCK_RE = re.compile(r"(?m)^[ \t]*([a-z]+)[ \t]*\{(.*?)\}", re.DOTALL)
def blocks(text: str, kind: str) -> list[str]:
    return [body for block_kind, body in BLOCK_RE.findall(text) if block_kind == kind]


def int_property(body: str, name: str) -> int:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(-?\d+)\s*;", body)
    if match is None:
        raise VerifyError(f"missing integer property {name}")
    return int(match.group(1))


def bool_property(body: str, name: str) -> bool:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(true|false)\s*;", body)
    if match is None:
        raise VerifyError(f"missing boolean property {name}")
    return match.group(1) == "true"


def float_property(body: str, name: str) -> float:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(-?\d+(?:\.\d+)?)\s*;", body)
    if match is None:
        raise VerifyError(f"missing float property {name}")
    return float(match.group(1))


def string_property(body: str, name: str) -> str:
    match = re.search(rf'\b{re.escape(name)}\s*=\s*"([^"]*)"\s*;', body)
    if match is None:
        raise VerifyError(f"missing string property {name}")
    return match.group(1)


def optional_int_property(body: str, name: str) -> int | None:
    match = re.search(rf"\b{re.escape(name)}\s*=\s*(-?\d+)\s*;", body)
    return None if match is None else int(match.group(1))


def wad_textmap(payload: bytes, map_name: str) -> str:
    if len(payload) < 12:
        raise VerifyError(f"{map_name}: WAD header is truncated")
    magic, lump_count, directory_offset = struct.unpack_from("<4sii", payload, 0)
    if magic != b"PWAD" or lump_count != 3:
        raise VerifyError(f"{map_name}: expected a three-lump PWAD")
    entries: list[tuple[int, int, str]] = []
    for index in range(lump_count):
        offset, size, raw_name = struct.unpack_from("<ii8s", payload, directory_offset + index * 16)
        entries.append((offset, size, raw_name.split(b"\0", 1)[0].decode("ascii")))
    expected = [map_name, "TEXTMAP", "ENDMAP"]
    if [name for _, _, name in entries] != expected:
        raise VerifyError(f"{map_name}: unexpected lump sequence")
    offset, size, _ = entries[1]
    return payload[offset : offset + size].decode("utf-8")


def verify_map(level: dict[str, Any], textmap: str, width: int, height: int) -> dict[str, int]:
    if 'user_brogue_role = 1;' in textmap:
        from tools.mapcompiler.terrain_geometry import verify_geometry
        counts = verify_geometry(level, textmap)
        sectors = blocks(textmap, 'sector')
        sector_cells = {i: (int_property(s, 'user_brogue_x'), int_property(s, 'user_brogue_y'))
                        for i, s in enumerate(sectors) if int_property(s, 'user_brogue_role') == 0}
        cells = {(int(c['x']), int(c['y'])): c for c in level['cells']}
        verify_things(level, width, height, sectors, sector_cells, blocks(textmap, 'thing'), set(cells), cells)
        return dict(sectorsPerMap=counts['primarySectors']+counts['controlSectors'],
                    verticesPerMap=counts['vertices'], linesPerMap=counts['lines'],
                    sidedefsPerMap=len(blocks(textmap, 'sidedef')))
    depth = int(level["depth"])
    cells = {(int(cell["x"]), int(cell["y"])): cell for cell in level["cells"]}
    geometry_cell_map = {position: cell for position, cell in cells.items() if cell_has_geometry(cell)}
    geometry_cells = set(geometry_cell_map)
    sector_blocks = blocks(textmap, "sector")
    vertex_blocks = blocks(textmap, "vertex")
    line_blocks = blocks(textmap, "linedef")
    side_blocks = blocks(textmap, "sidedef")
    thing_blocks = blocks(textmap, "thing")
    if not vertex_blocks:
        raise VerifyError(f"BRG{depth:02d}: map has no vertices")
    if len(sector_blocks) != len(geometry_cells):
        raise VerifyError(f"BRG{depth:02d}: expected {len(geometry_cells)} traversable/door sectors, found {len(sector_blocks)}")

    # Vertices are emitted on demand because contoured one-sided walls add
    # shoulder points outside the base grid. Coordinates must still be unique.
    vertices: list[tuple[int, int]] = []
    vertex_lookup: dict[tuple[int, int], int] = {}
    for index, body in enumerate(vertex_blocks):
        vertex = (int_property(body, "x"), int_property(body, "y"))
        if vertex in vertex_lookup:
            raise VerifyError(f"BRG{depth:02d}: duplicate vertex coordinate {vertex[0]},{vertex[1]}")
        vertex_lookup[vertex] = index
        vertices.append(vertex)
    line_edges: dict[tuple[int, int], int] = {}
    for index, body in enumerate(line_blocks):
        v1 = int_property(body, "v1")
        v2 = int_property(body, "v2")
        if v1 < 0 or v1 >= len(vertices) or v2 < 0 or v2 >= len(vertices):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} references an invalid vertex")
        if v1 == v2:
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has zero length")
        edge_key = (min(v1, v2), max(v1, v2))
        if edge_key in line_edges:
            raise VerifyError(f"BRG{depth:02d}: duplicate linedef edge {v1},{v2}")
        line_edges[edge_key] = index
        front_side = int_property(body, "sidefront")
        if front_side < 0 or front_side >= len(side_blocks):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has an invalid front sidedef")
        back_side = optional_int_property(body, "sideback")
        if back_side is not None and (back_side < 0 or back_side >= len(side_blocks)):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has an invalid back sidedef")

    if len(line_edges) != len(line_blocks):
        raise VerifyError(f"BRG{depth:02d}: line edge count does not match linedef count")

    sector_cells: dict[int, tuple[int, int]] = {}
    for index, body in enumerate(sector_blocks):
        x = int_property(body, "user_brogue_x")
        y = int_property(body, "user_brogue_y")
        if (x, y) not in cells:
            raise VerifyError(f"BRG{depth:02d}: sector {index} has unexpected coordinate {x},{y}")
        if (x, y) in sector_cells.values():
            raise VerifyError(f"BRG{depth:02d}: duplicate sector coordinate {x},{y}")
        if int_property(body, "user_brogue_depth") != depth:
            raise VerifyError(f"BRG{depth:02d}: sector {index} has the wrong depth metadata")
        expected_door = cell_has_door_geometry(cells[(x, y)])
        if bool(int_property(body, "user_brogue_door_sector")) != expected_door:
            raise VerifyError(f"BRG{depth:02d}: sector {index} has incorrect door metadata")
        if expected_door and int_property(body, "id") != 10000 + y * width + x:
            raise VerifyError(f"BRG{depth:02d}: door sector {index} has an unstable runtime tag")
        expected_ceiling = OPEN_VOID_CEILING_Z if depth > 1 else CAVE_CEILING_Z
        if int_property(body, "heightceiling") != expected_ceiling:
            raise VerifyError(f"BRG{depth:02d}: sector {index} does not share the unified ceiling height")
        if depth > 1:
            if string_property(body, "textureceiling") != OPEN_VOID_SKY_FLAT:
                raise VerifyError(f"BRG{depth:02d}: sector {index} does not use the open-void sky")
        sector_cells[index] = (x, y)
    if set(sector_cells.values()) != geometry_cells:
        raise VerifyError(f"BRG{depth:02d}: sector coordinate set does not match traversable JSON cells")

    sidedef_sector: list[int] = []
    for index, body in enumerate(side_blocks):
        if re.search(r"\btexture(?:upper|lower)\s*=", body):
            raise VerifyError(
                f"BRG{depth:02d}: sidedef {index} uses a nonstandard UDMF texture tier name"
            )
        # Parse every canonical tier even when it is intentionally empty. This
        # keeps misspelled keys from silently becoming GZDoom missing-texture
        # fallbacks at runtime.
        string_property(body, "texturetop")
        string_property(body, "texturebottom")
        string_property(body, "texturemiddle")
        sector = int_property(body, "sector")
        if sector < 0 or sector >= len(sector_blocks):
            raise VerifyError(f"BRG{depth:02d}: sidedef {index} references an invalid sector")
        sidedef_sector.append(sector)
    # Construct the exact expected contour/portal edge set from Brogue cells.
    # This validates cardinal connectivity and corner sealing without assuming
    # that every one-sided line remains a unit lattice edge.
    expected_edges: dict[tuple[tuple[int, int], tuple[int, int]], set[tuple[int, int]]] = {}
    neighbors = ((0, -1), (1, 0), (0, 1), (-1, 0))
    for x, y in sorted(geometry_cells):
        for side_index, (dx, dy) in enumerate(neighbors):
            neighbor = (x + dx, y + dy)
            points = map_side_points(
                height,
                x,
                y,
                side_index,
                cells[(x, y)],
                cells.get(neighbor),
                cells,
                geometry_cells,
            )
            for start, end in zip(points, points[1:]):
                edge = tuple(sorted((start, end)))
                expected_edges.setdefault(edge, set()).add((x, y))

    actual_edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    sector_degrees: dict[int, dict[int, int]] = {index: {} for index in sector_cells}
    for index, body in enumerate(line_blocks):
        front_side = int_property(body, "sidefront")
        back_side = optional_int_property(body, "sideback")
        front_sector = sidedef_sector[front_side]
        two_sided = bool_property(body, "twosided")
        if two_sided != (back_side is not None):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has inconsistent two-sided fields")
        if bool_property(body, "blocking") != (not two_sided):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has an incorrect passability boundary")

        if back_side is not None:
            front_floor = int_property(sector_blocks[front_sector], "heightfloor")
            back_sector = sidedef_sector[back_side]
            back_floor = int_property(sector_blocks[back_sector], "heightfloor")
            if front_floor != back_floor:
                for side_index in (front_side, back_side):
                    if string_property(side_blocks[side_index], "texturebottom") == "-":
                        raise VerifyError(
                            f"BRG{depth:02d}: floor-height transition on linedef {index} "
                            f"is missing its bottom texture"
                        )

        v1 = int_property(body, "v1")
        v2 = int_property(body, "v2")
        coordinate_edge = tuple(sorted((vertices[v1], vertices[v2])))
        if coordinate_edge in actual_edges:
            raise VerifyError(f"BRG{depth:02d}: duplicate physical edge {coordinate_edge}")
        actual_edges.add(coordinate_edge)
        expected_references = expected_edges.get(coordinate_edge)
        if expected_references is None:
            raise VerifyError(f"BRG{depth:02d}: linedef {index} is not part of the expected contour geometry")

        referenced_sectors = {front_sector}
        if back_side is not None:
            referenced_sectors.add(sidedef_sector[back_side])
        referenced_cells = {sector_cells[sector] for sector in referenced_sectors}
        if referenced_cells != expected_references:
            raise VerifyError(f"BRG{depth:02d}: linedef {index} sidedefs do not match its Brogue cells")
        if two_sided != (len(expected_references) == 2):
            raise VerifyError(f"BRG{depth:02d}: linedef {index} has an incorrect cardinal portal state")

        for sector in referenced_sectors:
            degrees = sector_degrees[sector]
            degrees[v1] = degrees.get(v1, 0) + 1
            degrees[v2] = degrees.get(v2, 0) + 1

    if actual_edges != set(expected_edges):
        missing = len(set(expected_edges) - actual_edges)
        extra = len(actual_edges - set(expected_edges))
        raise VerifyError(f"BRG{depth:02d}: contour edge set mismatch (missing={missing}, extra={extra})")
    for sector, degrees in sector_degrees.items():
        if not degrees or any(degree != 2 for degree in degrees.values()):
            raise VerifyError(f"BRG{depth:02d}: sector {sector} does not form a closed boundary loop")

    verify_things(level, width, height, sector_blocks, sector_cells, thing_blocks, geometry_cells, cells)
    return {
        "sectorsPerMap": len(sector_blocks),
        "verticesPerMap": len(vertex_blocks),
        "linesPerMap": len(line_blocks),
        "sidedefsPerMap": len(side_blocks),
    }



def verify_things(level, width, height, sector_blocks, sector_cells, thing_blocks, geometry_cells, cells):
    depth = int(level["depth"])
    thing_types = {int_property(body, "type"): body for body in thing_blocks}
    expected_up = level["upStairs"]
    expected_down = level["downStairs"]
    for thing_type, stair in ((15000, expected_up), (15001, expected_down)):
        body = thing_types.get(thing_type)
        if body is None:
            raise VerifyError(f"BRG{depth:02d}: missing stair thing {thing_type}")
        expected_x, expected_y = cell_center(width, height, int(stair["x"]), int(stair["y"]))
        if (int_property(body, "x"), int_property(body, "y")) != (expected_x, expected_y):
            raise VerifyError(f"BRG{depth:02d}: stair {thing_type} is not at its JSON coordinate")
    def expected_marker(stair: dict[str, Any]) -> tuple[int, int]:
        return cell_center(width, height, int(stair["x"]), int(stair["y"]))

    for thing_type, stair in ((15002, expected_up), (15003, expected_down)):
        body = thing_types.get(thing_type)
        if body is None:
            raise VerifyError(f"BRG{depth:02d}: missing visible stair marker {thing_type}")
        expected_x, expected_y = expected_marker(stair)
        if (int_property(body, "x"), int_property(body, "y")) != (expected_x, expected_y):
            raise VerifyError(f"BRG{depth:02d}: stair marker {thing_type} left its authoritative cell")

    door_markers = [body for body in thing_blocks if int_property(body, "type") in {15020, 15021}]
    expected_doors = {position for position, cell in cells.items() if cell_has_door_geometry(cell)}
    actual_doors = {
        (int_property(body, "arg0"), int_property(body, "arg1"))
        for body in door_markers
    }
    if actual_doors != expected_doors or len(door_markers) != len(expected_doors):
        raise VerifyError(f"BRG{depth:02d}: visual door markers do not match authoritative door cells")
    for body in door_markers:
        position = (int_property(body, "arg0"), int_property(body, "arg1"))
        symbol = layer_symbol(cells[position], "dungeon")
        expected_type = 15021 if symbol == "WOODEN_BARRICADE" else 15020
        if int_property(body, "type") != expected_type:
            raise VerifyError(f"BRG{depth:02d}: {symbol} at {position} has the wrong visual marker")
        if thing_type == 15002:
            up_position = (int(stair["x"]), int(stair["y"]))
            up_sector = next(index for index, position in sector_cells.items() if position == up_position)
            floor_z = int_property(sector_blocks[up_sector], "heightfloor")
            ceiling_z = int_property(sector_blocks[up_sector], "heightceiling")
            expected_scale = (ceiling_z - floor_z) / 128.0
            if abs(float_property(body, "scaley") - expected_scale) > 0.000001:
                raise VerifyError(f"BRG{depth:02d}: up ladder does not reach its ceiling hatch")
    player_start = thing_types.get(1)
    if player_start is None:
        raise VerifyError(f"BRG{depth:02d}: missing Player 1 start")
    expected_x, expected_y = cell_center(width, height, int(expected_up["x"]), int(expected_up["y"]))
    if (int_property(player_start, "x"), int_property(player_start, "y")) != (expected_x, expected_y):
        raise VerifyError(f"BRG{depth:02d}: Player 1 start is not on upstairs")

    stair_positions = {
        (int(expected_up["x"]), int(expected_up["y"])),
        (int(expected_down["x"]), int(expected_down["y"])),
    }
    expected_props: list[tuple[int, int, int, int, int]] = []
    game_seed = level.get("gameSeed", "")
    # Full exports keep the game seed at the document root; compile-package
    # passes it separately. The verifier receives it through a temporary field
    # installed by verify_package below.
    game_seed = level.get("_verifyGameSeed", game_seed)
    for position in sorted(geometry_cells):
        if position in stair_positions:
            continue
        placement = prop_placement(cells[position], game_seed, depth, width, height)
        if placement is not None:
            expected_props.append(
                (
                    int(placement["type"]),
                    int(placement["x"]),
                    int(placement["y"]),
                    int(placement["z"]),
                    int(placement["angle"]),
                )
            )
    prop_types = {rule[1] for rule in PROP_RULES.values()}
    actual_props = sorted(
        (
            int_property(body, "type"),
            int_property(body, "x"),
            int_property(body, "y"),
            int_property(body, "z"),
            int_property(body, "angle"),
        )
        for body in thing_blocks
        if int_property(body, "type") in prop_types
    )
    if actual_props != sorted(expected_props):
        raise VerifyError(f"BRG{depth:02d}: semantic prop placement does not match Brogue surface layers")

def verify_package(input_path: Path, package_path: Path, depth: int | None = None, map_name: str | None = None, startup: bool = False) -> dict[str, Any]:
    if startup and (depth is not None or map_name is not None):
        raise VerifyError('startup mode cannot be combined with standalone depth/map-name')
    try:
        model = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise VerifyError(f"could not read JSON input: {error}") from error
    if not isinstance(model, dict):
        raise VerifyError("JSON root is not an object")
    width, height, _ = validate_model(model)
    if depth is None:
        levels = model["levels"][:1] if startup else model["levels"]
        map_names = [f"BRG{int(level['depth']):02d}" for level in levels]
    else:
        if depth < 1 or depth > len(model["levels"]):
            raise VerifyError(f"requested depth {depth} is outside the exported level range")
        levels = [model["levels"][depth - 1]]
        map_names = [(map_name or "MAP01").upper()]
    for level in levels:
        level["_verifyGameSeed"] = str(model.get("seed", ""))
    with zipfile.ZipFile(package_path) as archive:
        if startup:
            expected_mapinfo = make_mapinfo([(f"BRG{int(level['depth']):02d}", int(level['depth'])) for level in model['levels']])
            if archive.read('MAPINFO').decode('utf-8') != expected_mapinfo:
                raise VerifyError('startup package lost depth metadata')
            if json.loads(archive.read('brogue-manifest.json')).get('startupOnly') is not True:
                raise VerifyError('not a startup package')
        expected_names = ["MAPINFO", "brogue-manifest.json"] + [f"maps/{name.lower() if depth is not None else name}.wad" for name in map_names]
        if archive.namelist() != expected_names:
            raise VerifyError("PK3 entry order or map set is not deterministic")
        counts = []
        for level, current_map_name in zip(levels, map_names):
            counts.append(verify_map(level, wad_textmap(archive.read(f"maps/{current_map_name.lower() if depth is not None else current_map_name}.wad"), current_map_name), width, height))
    for level in levels:
        level.pop("_verifyGameSeed", None)
    return {"maps": len(levels), **counts[0]}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--depth", type=int, help="verify one exported depth compiled as a standalone map")
    parser.add_argument("--map-name", default=None, help="standalone map marker; defaults to MAP01")
    parser.add_argument('--startup', action='store_true', help='verify the runtime bridge startup package')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify_package(args.input, args.package, args.depth, args.map_name, args.startup), separators=(",", ":")))
    except (OSError, zipfile.BadZipFile, VerifyError) as error:
        print(f"mapcompiler verify: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
