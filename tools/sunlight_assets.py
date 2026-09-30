"""Generate Project Broom's deterministic first-floor sunlight presentation assets."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]


def _ray_mesh() -> str:
    # A tapered octagonal shell reads as volume without the screen-filling
    # intersections produced by crossed translucent billboards.
    lines = ["# Original Project Broom sunlight shaft, CC0-1.0"]
    vertices: list[tuple[float, float, float]] = []
    sides = 8
    for index in range(sides):
        angle = math.tau * index / sides
        vertices.append((7 + math.cos(angle) * 9, 2, 3 + math.sin(angle) * 9))
        vertices.append((-7 + math.cos(angle) * 6, 223, -3 + math.sin(angle) * 6))
    for x, y, z in vertices:
        lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    for _ in range(sides):
        lines.extend(("vt 0 1", "vt 1 1", "vt 1 0", "vt 0 0"))
    for side in range(sides):
        nxt = (side + 1) % sides
        bottom, top = side * 2 + 1, side * 2 + 2
        next_bottom, next_top = nxt * 2 + 1, nxt * 2 + 2
        uv = side * 4 + 1
        lines.append(f"f {bottom}/{uv} {next_bottom}/{uv+1} {next_top}/{uv+2} {top}/{uv+3}")
    return "\n".join(lines) + "\n"


def generate(root: Path = ROOT) -> None:
    models = root / "mod/BrogueDoom/models/terrain"
    graphics = root / "mod/BrogueDoom/graphics"
    models.mkdir(parents=True, exist_ok=True)
    graphics.mkdir(parents=True, exist_ok=True)
    (models / "sun_ray.obj").write_text(_ray_mesh(), encoding="ascii", newline="\n")

    rock_source = graphics / "BRGROCK.png"
    if not rock_source.is_file():
        rock_source = ROOT / "mod/BrogueDoom/graphics/BRGROCK.png"
    rock = Image.open(rock_source).convert("RGB").resize((128, 128), Image.Resampling.LANCZOS)
    hole = ((64, 27), (78, 32), (91, 43), (94, 58), (87, 72), (91, 85),
            (75, 98), (59, 94), (45, 101), (34, 86), (37, 70), (28, 58), (38, 42), (51, 36))
    rim = tuple((64 + (x - 64) * 1.18, 64 + (y - 64) * 1.18) for x, y in hole)
    draw = ImageDraw.Draw(rock)
    draw.polygon(rim, fill=(12, 11, 10))
    sky = Image.new("RGB", (128, 128))
    sky.putdata([
        (int(126 + 52 * max(0.0, 1.0 - math.hypot(x - 61, y - 60) / 80)),
         int(168 + 48 * max(0.0, 1.0 - math.hypot(x - 61, y - 60) / 80)),
         int(187 + 42 * max(0.0, 1.0 - math.hypot(x - 61, y - 60) / 80)))
        for y in range(128) for x in range(128)
    ])
    mask = Image.new("L", (128, 128))
    ImageDraw.Draw(mask).polygon(hole, fill=255)
    rock.paste(sky, mask=mask.filter(ImageFilter.GaussianBlur(0.7)))
    draw = ImageDraw.Draw(rock)
    for start, end in (((35, 49), (12, 37)), ((39, 86), (17, 104)), ((82, 39), (108, 24)), ((88, 78), (113, 93))):
        draw.line((start, end), fill=(18, 16, 14), width=3)
    rock.save(graphics / "BRGSUNHO.png", optimize=False)

    image = Image.new("RGBA", (64, 256))
    pixels = []
    for y in range(256):
        vertical = math.sin(math.pi * (y + 0.5) / 256) ** 0.42
        for x in range(64):
            center = abs((x + 0.5) / 32 - 1)
            core = max(0.0, 1.0 - center ** 1.65)
            shimmer = 0.90 + 0.10 * math.sin(x * 0.73 + y * 0.057)
            alpha = round(128 * vertical * core * shimmer)
            pixels.append((255, 236, 184, alpha))
    image.putdata(pixels)
    image.save(graphics / "BRGSUNRY.png", optimize=False)


if __name__ == "__main__":
    generate()
