#!/usr/bin/env python3
"""Generate deterministic, low-poly OBJ stair markers for BrogueDoom."""

from __future__ import annotations

from pathlib import Path
import struct
import zlib


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "mod" / "BrogueDoom" / "models" / "stairs"


class ObjBuilder:
    def __init__(self, name: str) -> None:
        self.lines = [f"o {name}"]
        self.vertex_count = 0

    def box(
        self,
        name: str,
        forward1: float,
        lateral1: float,
        up1: float,
        forward2: float,
        lateral2: float,
        up2: float,
    ) -> None:
        self.lines.append(f"g {name}")
        # GZDoom's model matrix treats OBJ X as forward, OBJ Y as world-up,
        # and OBJ Z as lateral. Keep the generator API in semantic Doom-world
        # terms and perform that axis mapping explicitly here.
        vertices = (
            (forward1, up1, lateral1), (forward2, up1, lateral1),
            (forward2, up2, lateral1), (forward1, up2, lateral1),
            (forward1, up1, lateral2), (forward2, up1, lateral2),
            (forward2, up2, lateral2), (forward1, up2, lateral2),
        )
        for x, y, z in vertices:
            self.lines.append(f"v {x:g} {y:g} {z:g}")
        # One reusable full-texture UV square per box.
        self.lines.extend(("vt 0 0", "vt 1 0", "vt 1 1", "vt 0 1"))
        v = self.vertex_count + 1
        t = self.vertex_count // 2 + 1
        # Quads are deliberately planar and outward-wound.
        faces = (
            (v, v + 3, v + 2, v + 1),
            (v + 4, v + 5, v + 6, v + 7),
            (v, v + 1, v + 5, v + 4),
            (v + 1, v + 2, v + 6, v + 5),
            (v + 2, v + 3, v + 7, v + 6),
            (v + 3, v, v + 4, v + 7),
        )
        for a, b, c, d in faces:
            self.lines.append(f"f {a}/{t} {b}/{t + 1} {c}/{t + 2} {d}/{t + 3}")
        self.vertex_count += 8

    def write(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="ascii", newline="\n")


def upstairs() -> ObjBuilder:
    model = ObjBuilder("BrogueUpLadder")
    # The actor faces the open approach cell (+X), so the ladder sits against
    # the far wall at -X and presents its broad face to the player.
    model.box("left_rail", -28, -21, 0, -24, -16, 128)
    model.box("right_rail", -28, 16, 0, -24, 21, 128)
    for rung in range(11):
        up = 8 + rung * 11
        model.box(f"rung_{rung}", -30, -18, up, -22, 18, up + 3)
    return model


def up_hatch() -> ObjBuilder:
    model = ObjBuilder("BrogueUpHatch")
    # The thing's vertical UDMF scale places this dark underside immediately
    # below the stair cell's real ceiling, where the ladder rails terminate.
    model.box("hatch", -31, -24, 124, 16, 24, 127)
    return model


def downstairs() -> ObjBuilder:
    model = ObjBuilder("BrogueDownPitFrame")
    # A full-cell stone rim frames a dark opening. The short rails/rungs cross
    # the approach edge and visually disappear into that opening.
    model.box("rim_front", 20, -26, 0, 26, 26, 7)
    model.box("rim_back", -26, -26, 0, -20, 26, 7)
    model.box("rim_left", -20, -26, 0, 20, -20, 7)
    model.box("rim_right", -20, 20, 0, 20, 26, 7)
    model.box("ladder_left", -10, -13, 2, 22, -9, 6)
    model.box("ladder_right", -10, 9, 2, 22, 13, 6)
    for rung in range(5):
        x1 = -8 + rung * 7
        model.box(f"pit_rung_{rung}", x1, -11, 3, x1 + 3, 11, 6)
    return model


def down_void() -> ObjBuilder:
    model = ObjBuilder("BrogueDownPitVoid")
    model.box("void", -20, -20, 0.25, 20, 20, 0.5)
    return model


def fall_shaft() -> ObjBuilder:
    model = ObjBuilder("BrogueFallShaft")
    # A hollow 60x60 opening hangs immediately below the real destination
    # ceiling. Four dark walls establish depth and a recessed cap closes the
    # illusion without changing collision or the destination sector itself.
    model.box("north_wall", -30, -30, 0, 30, -22, 40)
    model.box("south_wall", -30, 22, 0, 30, 30, 40)
    model.box("west_wall", -30, -22, 0, -22, 22, 40)
    model.box("east_wall", 22, -22, 0, 30, 22, 40)
    model.box("dark_cap", -22, -22, 39, 22, 22, 40)
    return model


def write_rgba_png(path: Path, width: int, height: int, rows: list[bytes]) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    payload = b"".join(rows)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(payload, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def write_pit_texture(path: Path) -> None:
    """Write a tiny deterministic near-black RGBA PNG for the pit interior."""
    width = height = 64
    rows = []
    for y in range(height):
        row = bytearray([0])  # PNG filter: none
        for x in range(width):
            dx = x - (width - 1) / 2
            dy = y - (height - 1) / 2
            edge = min(1.0, (dx * dx + dy * dy) ** 0.5 / 45.0)
            grain = ((x * 17 + y * 31) % 5) - 2
            base = int(2 + 8 * edge)
            row.extend((max(0, base + grain), max(0, base + grain), base + 3, 255))
        rows.append(bytes(row))
    write_rgba_png(path, width, height, rows)


def write_chasm_cliff_texture(path: Path) -> None:
    """Write a full-height rocky cliff that darkens toward the abyss."""
    width, height = 64, 128
    cell_width = 16
    cell_height = 14

    def cell_hash(gx: int, gy: int) -> int:
        # X wraps so the generated cliff tiles without a vertical seam.
        wrapped_x = gx % (width // cell_width)
        value = (wrapped_x * 0x45D9F3B + gy * 0x119DE1F3 + 0xB0A6E) & 0xFFFFFFFF
        value ^= value >> 16
        value = (value * 0x45D9F3B) & 0xFFFFFFFF
        return value ^ (value >> 16)

    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            grid_x = x // cell_width
            grid_y = y // cell_height
            nearest = 1 << 30
            second = 1 << 30
            winner = 0
            for gy in range(grid_y - 1, grid_y + 2):
                for gx in range(grid_x - 1, grid_x + 2):
                    value = cell_hash(gx, gy)
                    center_x = gx * cell_width + 4 + value % 9
                    center_y = gy * cell_height + 3 + (value >> 8) % 9
                    dx = x - center_x
                    dy = y - center_y
                    distance = dx * dx + (dy * dy * 5) // 4
                    if distance < nearest:
                        second = nearest
                        nearest = distance
                        winner = value
                    elif distance < second:
                        second = distance
            grain = ((x * 17 + y * 31 + (winner & 31)) % 9) - 4
            depth_falloff = (y * 28) // (height - 1)
            stone = 58 - depth_falloff + ((winner >> 16) % 13) + grain
            if second - nearest < 28:
                stone -= 20
            # Break up the top silhouette with a narrow, irregular shadow line
            # while retaining visible rock immediately beneath the floor edge.
            lip_depth = 4 + ((x * 11 + (x // 7) * 5) % 6)
            if y == lip_depth:
                stone -= 12
            stone = max(18, min(68, stone))
            row.extend((stone, max(14, stone - 6), max(16, stone - 3), 255))
        rows.append(bytes(row))
    write_rgba_png(path, width, height, rows)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    upstairs().write(OUTPUT / "upstairs.obj")
    up_hatch().write(OUTPUT / "up_hatch.obj")
    downstairs().write(OUTPUT / "downstairs.obj")
    down_void().write(OUTPUT / "down_void.obj")
    fall_shaft().write(OUTPUT / "fall_shaft.obj")
    write_pit_texture(ROOT / "mod" / "BrogueDoom" / "graphics" / "BRGPIT.png")
    write_chasm_cliff_texture(ROOT / "mod" / "BrogueDoom" / "graphics" / "BRGCLIFF.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
