"""Extract crisp runtime fonts from Brogue CE's authoritative tile sheet."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "tooling" / "BrogueCE-compare" / "source-7f52dd9" / "bin" / "assets" / "tiles.png"
DEFAULT_OUTPUT = ROOT / "mod" / "BrogueDoom" / "graphics" / "fonts"
SOURCE_SIZE = (2048, 5568)
SOURCE_CELL = (128, 232)


def extract_glyph(sheet: Image.Image, codepoint: int, size: tuple[int, int]) -> Image.Image:
    column = codepoint % 16
    row = codepoint // 16
    left = column * SOURCE_CELL[0]
    top = row * SOURCE_CELL[1]
    glyph = sheet.crop((left, top, left + SOURCE_CELL[0], top + SOURCE_CELL[1])).convert("RGB")

    # Brogue's font tiles are grayscale on black. Preserve their original
    # coverage as alpha so GZDoom can color the same shapes per draw call.
    channels = glyph.split()
    coverage = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    coverage = coverage.resize(size, Image.Resampling.LANCZOS)
    result = Image.new("RGBA", size, (255, 255, 255, 0))
    result.putalpha(coverage)
    return result


def generate(source: Path, output: Path) -> None:
    sheet = Image.open(source)
    if sheet.size != SOURCE_SIZE:
        raise ValueError(f"unexpected Brogue tile sheet size {sheet.size}; expected {SOURCE_SIZE}")

    variants = {
        "ui": ("BFU", (12, 22)),
        "map": ("BFM", (5, 8)),
    }
    for directory, (prefix, size) in variants.items():
        destination = output / directory
        destination.mkdir(parents=True, exist_ok=True)
        for codepoint in range(33, 127):
            image = extract_glyph(sheet, codepoint, size)
            image.save(destination / f"{prefix}{codepoint:03d}.png", optimize=False, compress_level=9)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    generate(args.source.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
