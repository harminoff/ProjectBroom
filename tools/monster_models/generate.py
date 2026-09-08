"""Generate the complete deterministic Brogue monster presentation roster."""

from __future__ import annotations

import json
import math
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
BRIDGE = ROOT / "src" / "brogue-mapgen" / "bin" / "brogue-bridge.exe"
CATALOG = ROOT / "assets" / "monsters" / "brogue_monster_catalog.json"
REGISTRY = ROOT / "assets" / "monsters" / "brogue_monster_registry.json"
MODEL_DIR = ROOT / "mod" / "BrogueDoom" / "models" / "monsters"
GRAPHICS = ROOT / "mod" / "BrogueDoom" / "graphics"
ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue_monsters.zs"

# Authored assets are rebuilt by their own tool, never by the placeholder mesh
# generator. Keep bindings here so regenerating the catalog preserves the art.
CUSTOM_MODELS = {}

# Every non-player kind now has an explicit authored recipe and work card.
# Catalog regeneration binds these files but never overwrites authored meshes.
from tools.monster_models.bestiary import profiles
_profiles = profiles()
_catalog = json.loads(CATALOG.read_text(encoding='utf-8'))['kinds']
_ids = {k['symbol']:k['kind'] for k in _catalog}
for _symbol in _profiles:
    _slug = _symbol.removeprefix('MK_').lower()
    # Resolve IDs from the source-backed catalog; never from dictionary order.
    _kind = _ids[_symbol]
    CUSTOM_MODELS[_symbol] = {
        'skin': f'graphics/BRGM{_kind:02d}.png',
        'authoringSource': f'assets/monsters/sources/{_kind:02d}_{_slug}.blend',
        'generator': 'tools/monster_models/creatures.py',
        'rebuildCommand': f'python -m tools.monster_models.creatures --kind {_kind}',
        'workIndex': f'BRG-M{_kind:02d}',
        'family': _profiles[_symbol]['recipe'],
        'authoredDimensions': _profiles[_symbol]['dimensions'],
    }


from tools.monster_models.skeletal_registry import profiles as skeletal_profiles, generate as generate_skeletal_bindings
SKELETAL = {row['symbol']: row for row in skeletal_profiles()}
for symbol, row in SKELETAL.items():
    CUSTOM_MODELS[symbol] = {
        **CUSTOM_MODELS.get(symbol, {}),
        'runtimeFilename': row['model'], 'skin': row['skin'],
        'authoringSource': row['source'],
        'generator': 'tools/monster_models/'+row['module']+'.py',
        'rebuildCommand': 'python -m tools.monster_models.'+row['module'],
        'animationManifest': row['manifest'],
    }
    _animated = json.loads((ROOT/row['manifest']).read_text())
    if 'dimensions' in _animated:
        CUSTOM_MODELS[symbol]['authoredDimensions'] = _animated['dimensions']


class Mesh:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[int, ...]] = []

    def box(self, x: float, y: float, z: float, sx: float, sy: float, sz: float) -> None:
        base = len(self.vertices) + 1
        self.vertices.extend((x + dx * sx, y + dy * sy, z + dz * sz)
                             for dx, dy, dz in ((-1, 0, -1), (1, 0, -1), (1, 1, -1), (-1, 1, -1),
                                                (-1, 0, 1), (1, 0, 1), (1, 1, 1), (-1, 1, 1)))
        self.faces.extend(tuple(base + i for i in face) for face in
                          ((0, 1, 2, 3), (5, 4, 7, 6), (4, 0, 3, 7),
                           (1, 5, 6, 2), (3, 2, 6, 7), (4, 5, 1, 0)))

    def bipyramid(self, x: float, y: float, z: float, radius: float, height: float, sides: int = 6) -> None:
        base = len(self.vertices) + 1
        self.vertices.append((x, y, z))
        self.vertices.append((x, y + height, z))
        for i in range(sides):
            angle = i * math.tau / sides
            self.vertices.append((x + math.cos(angle) * radius, y + height * .48,
                                  z + math.sin(angle) * radius))
        for i in range(sides):
            a, b = base + 2 + i, base + 2 + (i + 1) % sides
            self.faces.extend(((base, b, a), (base + 1, a, b)))

    def write(self, path: Path, name: str, uv: tuple[float, float]) -> None:
        lines = [f"o {name}"]
        lines.extend(f"v {x:.4f} {y:.4f} {z:.4f}" for x, y, z in self.vertices)
        lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
        lines.extend("f " + " ".join(f"{index}/1" for index in face) for face in self.faces)
        path.write_text("\n".join(lines) + "\n", encoding="ascii")


def slug(symbol: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", symbol.removeprefix("MK_").lower()).strip("_")


def family(symbol: str) -> str:
    value = symbol.lower()
    if any(word in value for word in ("turret", "totem", "sentinel", "guardian")):
        return "construct"
    if any(word in value for word in ("bat", "wisp", "bloat", "dar_", "phoenix", "dragon")):
        return "flying"
    if any(word in value for word in ("eel", "naga", "salamander", "worm", "kraken")):
        return "serpentine"
    if any(word in value for word in ("spider", "centipede", "scorpion")):
        return "arthropod"
    if any(word in value for word in ("jelly", "mound", "fury", "horror", "phantom")):
        return "amorphous"
    if any(word in value for word in ("rat", "jackal", "toad", "monkey", "unicorn")):
        return "beast"
    return "humanoid"


def make_mesh(kind: dict) -> Mesh:
    mesh = Mesh()
    index = kind["kind"]
    large = kind["isLarge"]
    scale = 1.18 if large else .88
    variant = (index % 5) * .7
    shape = family(kind["symbol"])
    if shape == "humanoid":
        mesh.box(0, 8 * scale, 0, 6 * scale, 18 * scale, 4.5 * scale)
        mesh.bipyramid(0, 28 * scale, 0, (7 + variant) * scale, 13 * scale)
        mesh.box(-4 * scale, 0, 0, 2.2 * scale, 10 * scale, 2.4 * scale)
        mesh.box(4 * scale, 0, 0, 2.2 * scale, 10 * scale, 2.4 * scale)
        mesh.box(-8 * scale, 9 * scale, 0, 2 * scale, 15 * scale, 2 * scale)
        mesh.box(8 * scale, 9 * scale, 0, 2 * scale, 15 * scale, 2 * scale)
    elif shape == "beast":
        mesh.box(0, 7 * scale, 0, 13 * scale, 11 * scale, 6 * scale)
        mesh.bipyramid(14 * scale, 9 * scale, 0, 6 * scale, 10 * scale)
        for x in (-9, 9):
            for z in (-4, 4):
                mesh.box(x * scale, 0, z * scale, 2 * scale, 8 * scale, 2 * scale)
        mesh.box(-17 * scale, 10 * scale, 0, 7 * scale, 2 * scale, 1.5 * scale)
    elif shape == "serpentine":
        for segment in range(5):
            mesh.bipyramid((segment - 2) * 8 * scale, (segment % 2) * 2, 0,
                           (7 - segment * .45) * scale, (12 + variant) * scale)
        mesh.bipyramid(20 * scale, 4, 0, 8 * scale, 16 * scale)
    elif shape == "flying":
        mesh.bipyramid(0, 13 * scale, 0, 10 * scale, 20 * scale)
        mesh.box(-15 * scale, 19 * scale, 0, 14 * scale, 2 * scale, 8 * scale)
        mesh.box(15 * scale, 19 * scale, 0, 14 * scale, 2 * scale, 8 * scale)
    elif shape == "arthropod":
        mesh.bipyramid(0, 5 * scale, 0, 12 * scale, 12 * scale, 8)
        mesh.bipyramid(13 * scale, 5 * scale, 0, 8 * scale, 11 * scale, 6)
        for side in (-1, 1):
            for leg in range(4):
                mesh.box((4 + leg * 2) * side * scale, 3 * scale, (leg - 1.5) * 5 * scale,
                         (8 + leg) * scale, 1.2 * scale, 1.2 * scale)
    elif shape == "construct":
        mesh.box(0, 0, 0, 12 * scale, 8 * scale, 12 * scale)
        mesh.box(0, 8 * scale, 0, 8 * scale, 22 * scale, 8 * scale)
        mesh.bipyramid(0, 30 * scale, 0, 12 * scale, (9 + variant) * scale, 4)
    else:
        mesh.bipyramid(0, 0, 0, (14 + variant) * scale, 27 * scale, 8)
        mesh.bipyramid(5 * scale, 15 * scale, 0, 8 * scale, 15 * scale, 6)
    # Deterministic silhouette ornaments make closely related catalog entries distinct.
    for ornament in range(index % 3):
        x = (-1 if ornament == 0 else 1) * (7 + ornament * 3) * scale
        mesh.bipyramid(x, 25 * scale, 0, 2.5 * scale, (8 + index % 4) * scale, 4)
    return mesh


def png_chunk(name: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)


def write_atlas(kinds: list[dict]) -> None:
    size, columns = 512, 8
    rows = math.ceil(len(kinds) / columns)
    pixels = bytearray()
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            col, grid_row = x * columns // size, y * rows // size
            index = min(grid_row * columns + col, len(kinds) - 1)
            color = kinds[index]["color"]
            rgb = [max(18, min(255, round(color[channel] * 2.25))) for channel in ("red", "green", "blue")]
            row.extend((*rgb, 255))
        pixels.extend(row)
    payload = b"\x89PNG\r\n\x1a\n"
    payload += png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    payload += png_chunk(b"IDAT", zlib.compress(bytes(pixels), 9))
    payload += png_chunk(b"IEND", b"")
    (GRAPHICS / "BRGMON.png").write_bytes(payload)


def main() -> None:
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHICS.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(BRIDGE), "--dump-monster-catalog", str(CATALOG)], check=True, cwd=ROOT)
    source = json.loads(CATALOG.read_text(encoding="utf-8"))
    kinds = source["kinds"]
    entries = []
    modeldef = ["// Generated by tools/monster_models/generate.py; do not edit by hand.", ""]
    zscript = ["// Generated by tools/monster_models/generate.py; do not edit by hand.", "",
               "class BrogueMonsterProxyBase : Actor", "{", "    Default",
               "    {", "        Radius 1; Height 1; Scale 1.0;",
               "        +NOBLOCKMAP; +NOGRAVITY; +NOINTERACTION; +NOTONAUTOMAP;",
               "    }", "    States { Spawn: BRM0 A -1; Stop; }", "}", ""]
    zscript.append('#include "brogue_rat_skeleton.zs"')
    rows, columns = math.ceil(len(kinds) / 8), 8
    for kind in kinds:
        index = kind["kind"]
        model = f"{index:02d}_{slug(kind['symbol'])}.obj"
        class_name = f"BrogueMonsterK{index:02d}"
        uv = (((index % columns) + .5) / columns, 1 - ((index // columns) + .5) / rows)
        custom = CUSTOM_MODELS.get(kind["symbol"])
        if custom: model=custom.get('runtimeFilename',model)
        if custom:
            if not (MODEL_DIR / model).is_file() or not (GRAPHICS / Path(custom["skin"]).name).is_file():
                raise FileNotFoundError(
                    f"Missing authored asset for {kind['symbol']}; run {custom.get('rebuildCommand', 'python '+custom['generator'])} first."
                )
        else:
            make_mesh(kind).write(MODEL_DIR / model, class_name, uv)
        entries.append({**kind, "family": family(kind["symbol"]), "class": class_name, "model": model,
                        **(custom or {})})
        skin = custom["skin"] if custom else "graphics/BRGMON.png"
        visual_scale = SKELETAL.get(kind['symbol'], {}).get('visualScale', 1.0)
        modeldef.extend((f"Model {class_name}", "{", '    Path "models/monsters"',
                         f'    Model 0 "{model}"', f'    Skin 0 "{skin}"',
                         f"    Scale {visual_scale} {visual_scale} {visual_scale}", "    FrameIndex BRM0 A 0 0",
                         *(('    BaseFrame',) if kind['symbol'] in SKELETAL else ()), "}", ""))
        if kind["symbol"] in SKELETAL:
            base_class=SKELETAL[kind["symbol"]]["baseClass"]
            zscript.extend([f"class {class_name} : {base_class}", "{",
                "    Default { +DECOUPLEDANIMATIONS; }",
                '    States { Spawn: BRM0 A 0; BRM0 A -1 A_SetAnimation("'+SKELETAL[kind['symbol']]['clips'][0]+'", -1, -1, -1, -1, 1, SAF_LOOP); Stop; }', "}"])
            captive=SKELETAL[kind['symbol']].get('captivity')
            if captive:
                modeldef.extend((f"Model {captive['class']}", "{", '    Path "models/monsters"',
                    f'    Model 0 "{captive["model"]}"', f'    Skin 0 "{skin}"',
                    f'    Scale {visual_scale} {visual_scale} {visual_scale}', '    FrameIndex BRM0 A 0 0', '    BaseFrame', '}', ''))
                zscript.extend([f'class {captive["class"]} : {class_name}', '{',
                    '    States { Spawn: BRM0 A 0; BRM0 A -1 A_SetAnimation("'+captive['idle']+'", -1, -1, -1, -1, 1, SAF_LOOP); Stop; }', '}'])
        else: zscript.append(f"class {class_name} : BrogueMonsterProxyBase {{}}")
    registry = {"schemaVersion": 1, "bridgeApiVersion": source["bridgeApiVersion"],
                "catalogCount": len(kinds), "nonPlayerModelCount": len(kinds) - 1,
                "presentationModelCount": len(kinds), "monsters": entries}
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    (MODEL_DIR / "MODELDEF.txt").write_text("\n".join(modeldef), encoding="utf-8")
    ZSCRIPT.write_text("\n".join(zscript) + "\n", encoding="utf-8")
    write_atlas(kinds)
    generate_skeletal_bindings()
    print(f"Generated {len(kinds) - 1} gameplay monsters plus the hallucination/player presentation form.")


if __name__ == "__main__":
    main()
