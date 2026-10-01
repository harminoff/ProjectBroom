"""Generate original, deterministic molten-lava presentation assets.

These textures are presentation only. Brogue CE continues to own lava identity,
height, damage, movement, and all other gameplay behavior.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GRAPHICS = ROOT / "mod" / "BrogueDoom" / "graphics"


def field(x: float, y: float, phase: float = 0.0) -> float:
    return (
        0.42 * math.sin(x * math.tau * 2.0 + math.sin(y * math.tau * 1.7 + phase))
        + 0.31 * math.sin(y * math.tau * 3.0 - x * math.tau * 1.3 + phase * 1.7)
        + 0.19 * math.sin((x + y) * math.tau * 7.0 - phase * 0.7)
        + 0.08 * math.sin((x * 5.0 - y * 4.0) * math.tau + phase * 2.2)
    )


def write_surface() -> None:
    width = height = 1024
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            u, v = x / width, y / height
            n = field(u, v)
            crust = max(0.0, min(1.0, (n + 0.22) * 1.65))
            hot = max(0.0, min(1.0, 0.5 + 0.5 * field(u, v, 1.9)))
            vein = max(0.0, 1.0 - abs(n) * 7.0)
            pool = 0.35 + 0.65 * hot
            r = 92 + 120 * pool + 38 * vein
            g = 4 + 34 * pool + 150 * vein
            b = 1 + 5 * pool
            r = r * (1.0 - 0.78 * crust) + 24 * crust
            g = g * (1.0 - 0.92 * crust) + 10 * crust
            b = b * (1.0 - 0.92 * crust) + 7 * crust
            pixels[x, y] = (round(min(255, r)), round(min(255, g)), round(min(255, b)))
    image.save(GRAPHICS / "BRGLAVA.png", optimize=False, compress_level=9)

    mask = Image.new("L", (width, height))
    mask_pixels = mask.load()
    for y in range(height):
        for x in range(width):
            u, v = x / width, y / height
            n = field(u, v)
            crust = max(0.0, min(1.0, (n + 0.22) * 1.65))
            hot = max(0.0, min(1.0, 0.5 + 0.5 * field(u, v, 1.9)))
            vein = max(0.0, 1.0 - abs(n) * 7.0)
            mask_pixels[x, y] = round(255 * max(0.0, (1.0 - crust) * (0.2 + 0.55 * hot + 0.45 * vein)))
    mask.save(GRAPHICS / "BRGLAVA_BM.png", optimize=False, compress_level=9)


def write_lips() -> None:
    width, height = 64, 128
    for frame in range(8):
        image = Image.new("RGB", (width, height))
        pixels = image.load()
        for y in range(height):
            for x in range(width):
                wave = math.sin((x / width) * math.tau * 2.5 + frame * 0.55)
                channel = math.sin((x / width) * math.tau * 5.0 - frame * 0.8)
                edge = max(0.0, min(1.0, 0.5 + 0.5 * (wave * 0.7 + channel * 0.3)))
                if y < 44:
                    shade = 24 + int(22 * edge)
                    color = (shade + 8, shade, shade - 2)
                elif y < 92:
                    glow = edge * (1.0 - abs(y - 68) / 28.0)
                    color = (round(55 + 185 * glow), round(10 + 70 * glow), round(3 + 10 * glow))
                else:
                    fade = max(0.0, 1.0 - (y - 92) / 36.0)
                    color = (round(28 + 90 * fade * edge), round(5 + 28 * fade * edge), 2)
                pixels[x, y] = color
        # Doom lump names are limited to eight characters.
        image.save(GRAPHICS / f"PMLIP{frame:03d}.png", optimize=False, compress_level=9)


if __name__ == "__main__":
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    write_surface()
    write_lips()
