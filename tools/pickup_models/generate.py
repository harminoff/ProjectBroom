#!/usr/bin/env python3
"""Generate the complete Brogue pickup model/catalog presentation layer.

The authoritative item state remains in Brogue. These compact OBJ models are
presentation-only projections selected by category/kind (or a generic model
while Brogue considers an identifiable kind unknown).
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
MODEL_DIR = ROOT / "mod" / "BrogueDoom" / "models" / "pickups"
REGISTRY_PATH = ROOT / "assets" / "items" / "brogue_pickup_registry.json"
ZSCRIPT_PATH = ROOT / "mod" / "BrogueDoom" / "brogue_pickups.zs"
MODELDEF_PATH = MODEL_DIR / "MODELDEF.txt"


@dataclass(frozen=True)
class Category:
    symbol: str
    value: int
    names: tuple[str, ...]
    material: str
    hidden_identity: bool = False


CATEGORIES = (
    Category("FOOD", 1, ("ration of food", "mango"), "leather"),
    Category("WEAPON", 2, ("dagger", "sword", "broadsword", "whip", "rapier", "flail", "mace", "war hammer", "spear", "war pike", "axe", "war axe", "dart", "incendiary dart", "javelin"), "metal"),
    Category("ARMOR", 4, ("leather armor", "scale mail", "chain mail", "banded mail", "splint mail", "plate armor"), "metal"),
    Category("POTION", 8, ("life", "strength", "telepathy", "levitation", "detect magic", "speed", "fire immunity", "invisibility", "caustic gas", "paralysis", "hallucination", "confusion", "incineration", "darkness", "descent", "creeping death"), "glass", True),
    Category("SCROLL", 16, ("enchanting", "identify", "teleportation", "remove curse", "recharging", "protect armor", "protect weapon", "sanctuary", "magic mapping", "negation", "shattering", "discord", "aggravate monsters", "summon monsters"), "paper", True),
    Category("STAFF", 32, ("lightning", "firebolt", "poison", "tunneling", "blinking", "entrancement", "obstruction", "discord", "conjuration", "healing", "haste", "protection"), "wood", True),
    Category("WAND", 64, ("teleportation", "slowness", "polymorphism", "negation", "domination", "beckoning", "plenty", "invisibility", "empowerment"), "wood", True),
    Category("RING", 128, ("clairvoyance", "stealth", "regeneration", "transference", "light", "awareness", "wisdom", "reaping"), "gold", True),
    Category("CHARM", 256, ("health", "protection", "haste", "fire immunity", "invisibility", "telepathy", "levitation", "shattering", "guardian", "teleportation", "recharging", "negation"), "gold"),
    Category("GOLD", 512, ("gold",), "gold"),
    Category("AMULET", 1024, ("Amulet of Yendor",), "gold"),
    Category("GEM", 2048, ("lumenstone",), "crystal"),
    Category("KEY", 4096, ("door key", "cage key", "crystal orb"), "metal"),
)


# Atlas coordinates use OBJ's bottom-left origin. The generated image is 4x2.
UV = {
    "metal": (0.00, 0.50, 0.25, 1.00),
    "wood": (0.25, 0.50, 0.50, 1.00),
    "paper": (0.50, 0.50, 0.75, 1.00),
    "leather": (0.75, 0.50, 1.00, 1.00),
    "glass": (0.00, 0.00, 0.25, 0.50),
    "gold": (0.25, 0.00, 0.50, 0.50),
    "crystal": (0.50, 0.00, 0.75, 0.50),
    "fruit": (0.75, 0.00, 1.00, 0.50),
}


class Mesh:
    def __init__(self, name: str) -> None:
        self.name = name
        self.vertices: list[tuple[float, float, float]] = []
        self.uvs: list[tuple[float, float]] = []
        self.faces: list[tuple[tuple[int, int], ...]] = []

    def face(self, points: list[tuple[float, float, float]], material: str) -> None:
        u0, v0, u1, v1 = UV[material]
        coords = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
        face: list[tuple[int, int]] = []
        for point, uv in zip(points, coords):
            self.vertices.append(point)
            self.uvs.append(uv)
            face.append((len(self.vertices), len(self.uvs)))
        self.faces.append(tuple(face))

    def box(self, x: float, y: float, z: float, sx: float, sy: float, sz: float, material: str) -> None:
        x0, x1 = x - sx / 2, x + sx / 2
        y0, y1 = y, y + sy
        z0, z1 = z - sz / 2, z + sz / 2
        self.face([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)], material)
        self.face([(x1,y0,z1),(x0,y0,z1),(x0,y1,z1),(x1,y1,z1)], material)
        self.face([(x0,y0,z1),(x0,y0,z0),(x0,y1,z0),(x0,y1,z1)], material)
        self.face([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)], material)
        self.face([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)], material)
        self.face([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)], material)

    def cylinder(self, x: float, y: float, z: float, radius: float, height: float, material: str, sides: int = 10) -> None:
        for i in range(sides):
            a0, a1 = 2 * math.pi * i / sides, 2 * math.pi * (i + 1) / sides
            p0 = (x + radius*math.cos(a0), y, z + radius*math.sin(a0))
            p1 = (x + radius*math.cos(a1), y, z + radius*math.sin(a1))
            q1 = (p1[0], y + height, p1[2])
            q0 = (p0[0], y + height, p0[2])
            self.face([p0,p1,q1,q0], material)
        ring0 = [(x + radius*math.cos(2*math.pi*i/sides), y, z + radius*math.sin(2*math.pi*i/sides)) for i in range(sides)]
        ring1 = [(p[0], y + height, p[2]) for p in ring0]
        for i in range(1, sides - 1):
            self.face([ring0[0], ring0[i], ring0[i+1], ring0[i+1]], material)
            self.face([ring1[0], ring1[i+1], ring1[i], ring1[i]], material)

    def sphere(self, x: float, y: float, z: float, radius: float, material: str, rings: int = 5, sides: int = 10) -> None:
        for r in range(rings):
            p0 = -math.pi/2 + math.pi*r/rings
            p1 = -math.pi/2 + math.pi*(r+1)/rings
            for i in range(sides):
                a0, a1 = 2*math.pi*i/sides, 2*math.pi*(i+1)/sides
                def point(phi: float, angle: float) -> tuple[float,float,float]:
                    return (x + radius*math.cos(phi)*math.cos(angle), y + radius + radius*math.sin(phi), z + radius*math.cos(phi)*math.sin(angle))
                self.face([point(p0,a0),point(p0,a1),point(p1,a1),point(p1,a0)], material)

    def torus(self, x: float, y: float, z: float, major: float, minor: float, material: str, segments: int = 12) -> None:
        for i in range(segments):
            a0, a1 = 2*math.pi*i/segments, 2*math.pi*(i+1)/segments
            for j in range(6):
                b0, b1 = 2*math.pi*j/6, 2*math.pi*(j+1)/6
                def point(a: float, b: float) -> tuple[float,float,float]:
                    radial = major + minor*math.cos(b)
                    return (x + radial*math.cos(a), y + minor + minor*math.sin(b), z + radial*math.sin(a))
                self.face([point(a0,b0),point(a1,b0),point(a1,b1),point(a0,b1)], material)

    def write(self, path: Path) -> None:
        lines = [f"o {self.name}"]
        lines.extend(f"v {x:.4f} {y:.4f} {z:.4f}" for x,y,z in self.vertices)
        lines.extend(f"vt {u:.6f} {v:.6f}" for u,v in self.uvs)
        lines.extend("f " + " ".join(f"{vi}/{ti}" for vi,ti in face) for face in self.faces)
        path.write_text("\n".join(lines) + "\n", encoding="ascii")


def class_name(category: int, kind: int | None) -> str:
    return f"BroguePickupC{category:04d}{'Generic' if kind is None else f'K{kind:02d}'}"


def model_name(category: Category, kind: int | None) -> str:
    suffix = "generic" if kind is None else f"{kind:02d}"
    return f"{category.symbol.lower()}_{suffix}.obj"


def build_legacy_model(category: Category, kind: int | None) -> Mesh:
    k = 0 if kind is None else kind
    mesh = Mesh(class_name(category.value, kind))
    symbol = category.symbol
    if symbol == "FOOD":
        if k == 1:
            mesh.sphere(0, 1, 0, 5.5, "fruit"); mesh.box(0, 11, 0, 1.5, 4, 1.5, "wood")
        else:
            mesh.box(0, 0, 0, 12, 8, 9, "leather"); mesh.box(0, 8, 0, 10, 2, 7, "paper")
    elif symbol == "WEAPON":
        length = 18 + (k % 3) * 4
        if k == 3:  # whip
            for i in range(7): mesh.box(-12+i*4, 1+i*0.6, math.sin(i*.8)*4, 4.5, 1.5, 1.5, "leather")
        elif k == 5:  # flail
            mesh.box(-7, 1, 0, 16, 3, 3, "wood"); mesh.box(4, 2, 0, 7, 1, 1, "metal"); mesh.sphere(10, 0, 0, 4.5, "metal")
        elif k in (6,7):
            mesh.box(-6, 1, 0, 16, 3, 3, "wood"); mesh.box(5, 0, 0, 7+(k==7)*5, 8, 6, "metal")
        elif k in (10,11):
            mesh.box(-5, 1, 0, 18+(k==11)*5, 3, 3, "wood"); mesh.box(7, 0, 0, 9, 10+(k==11)*3, 3, "metal")
        elif k >= 12:
            mesh.box(0, 1, 0, 12+(k-12)*5, 2, 2, "metal"); mesh.box(7+(k-12)*2, 0, 0, 4, 4, 1, "metal")
        else:
            mesh.box(-length/3, 1, 0, length/2, 3, 3, "wood")
            mesh.box(1, 1, 0, 3, 5, 10 if k in (8,9) else 8, "gold")
            mesh.box(length/3, 1, 0, length, 2.5+(k%3), 4+(k%2), "metal")
    elif symbol == "ARMOR":
        width, height = 14 + k*1.2, 10 + k*1.5
        mesh.box(0, 0, 0, width, height, 5, "leather" if k == 0 else "metal")
        mesh.box(-width*.55, 2, 0, 4, height*.65, 5, "metal"); mesh.box(width*.55, 2, 0, 4, height*.65, 5, "metal")
        for band in range(1 + k//2): mesh.box(0, 2+band*3, -3, width*.9, 1, 1, "gold" if k>3 else "metal")
    elif symbol == "POTION":
        mesh.sphere(0, 0, 0, 6, "glass"); mesh.cylinder(0, 10, 0, 2.6, 5, "glass", 8); mesh.cylinder(0, 15, 0, 3.2, 2, "wood", 8)
    elif symbol == "SCROLL":
        mesh.box(0, 1, 0, 18, 2, 11, "paper"); mesh.cylinder(-9, 0, 0, 2.2, 5, "wood", 8); mesh.cylinder(9, 0, 0, 2.2, 5, "wood", 8)
        for mark in range(2 + k % 4): mesh.box(-5+mark*4, 3, -2+(mark%2)*4, 2, 0.8, 4, "gold")
    elif symbol in ("STAFF", "WAND"):
        long = symbol == "STAFF"; length = 32 if long else 18
        mesh.box(-2, 1, 0, length, 3 if long else 2, 3 if long else 2, "wood")
        mesh.sphere(length/2-1, 1, 0, 4+(k%3), "crystal", 4, 8)
        for prong in range(k % 3): mesh.box(length/2-2, 1, -5+prong*5, 6, 2, 1.5, "gold")
    elif symbol == "RING":
        mesh.torus(0, 1, 0, 6, 1.5, "gold"); mesh.sphere(0, 3, 0, 2.5+(k%3)*.5, "crystal", 3, 6)
    elif symbol == "CHARM":
        mesh.cylinder(0, 1, 0, 7, 2.5, "gold", 12); mesh.sphere(0, 3, 0, 3+(k%3), "crystal", 3, 6)
        mesh.torus(0, 5, 0, 8, .7, "gold", 12)
    elif symbol == "GOLD":
        for i,(x,z,r) in enumerate(((-5,-2,4),(2,-4,5),(5,3,4),(-2,4,3))): mesh.sphere(x, 0 if i else 1, z, r, "gold", 3, 8)
    elif symbol == "AMULET":
        mesh.torus(0, 1, 0, 9, .8, "gold", 14); mesh.sphere(0, 2, 0, 6, "crystal", 4, 8); mesh.cylinder(0, 7, 0, 2, 3, "gold", 8)
    elif symbol == "GEM":
        mesh.sphere(0, 0, 0, 8, "crystal", 4, 8)
    elif symbol == "KEY":
        if k == 2:
            mesh.sphere(0, 1, 0, 8, "crystal", 4, 8); mesh.torus(0, 2, 0, 9, 1, "gold", 12)
        else:
            mesh.torus(-8, 1, 0, 5, 1.5, "metal", 10); mesh.box(3, 1, 0, 18, 3, 3, "metal")
            for tooth in range(2+k): mesh.box(8+tooth*3, 0, 2, 2, 5+tooth, 2, "metal")
    else:
        mesh.box(0, 0, 0, 10, 10, 10, category.material)
    return mesh


def build_model(category: Category, kind: int | None):
    from tools.pickup_models.detailed import Model
    return Model(category, kind)


def main() -> None:
    from tools.pickup_models.detailed import atlas_bytes
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = []
    models = []
    # Do not overwrite BRGITEMS: held-weapon target markers also use that atlas.
    (ROOT / 'mod/BrogueDoom/graphics/BRGPICKS.png').write_bytes(atlas_bytes())
    zscript = ["// Generated by tools/pickup_models/generate.py; do not edit by hand.", ""]
    modeldef = ["// Generated by tools/pickup_models/generate.py; do not edit by hand.", ""]

    zscript.extend([
        "class BroguePickupProxyBase : Actor",
        "{",
        "    Default",
        "    {",
        "        Radius 1; Height 1; Scale 1.0;",
        "        +NOBLOCKMAP; +NOGRAVITY; +NOINTERACTION; +NOTONAUTOMAP;",
        "    }",
        "    States { Spawn: ITM0 A -1; Stop; }",
        "}",
        "",
    ])

    for category in CATEGORIES:
        variants: list[int | None] = list(range(len(category.names)))
        if category.hidden_identity:
            variants.insert(0, None)
        for kind in variants:
            cls = class_name(category.value, kind)
            filename = model_name(category, kind)
            model = build_model(category, kind)
            model.write(MODEL_DIR / filename)
            models.append({'category':category.value,'categorySymbol':category.symbol,'kind':kind,
                           'name':category.names[kind] if kind is not None else 'unidentified '+category.symbol.lower(),
                           'class':cls,'model':filename,**model.metadata()})
            zscript.extend([f"class {cls} : BroguePickupProxyBase {{}}", ""])
            modeldef.extend([
                f"Model {cls}",
                "{",
                '    Path "models/pickups"',
                f'    Model 0 "{filename}"',
                '    Skin 0 "graphics/BRGPICKS.png"',
                "    Scale 1.0 1.0 1.0",
                "    FrameIndex ITM0 A 0 0",
                "}",
                "",
            ])
        for kind, name in enumerate(category.names):
            records.append({
                "category": category.value,
                "categorySymbol": category.symbol,
                "kind": kind,
                "name": name,
                "class": class_name(category.value, kind),
                "genericClass": class_name(category.value, None) if category.hidden_identity else None,
                "identityHiddenUntilKnown": category.hidden_identity,
                "model": model_name(category, kind),
                "authoringSource": "assets/items/pickups.blend",
                "art": next(m for m in models if m['category']==category.value and m['kind']==kind),
            })

    registry = {
        "schemaVersion": 2,
        "source": "Brogue CE local Rogue.h and Globals.c item catalogs",
        "itemKindCount": len(records),
        "atlas": "mod/BrogueDoom/graphics/BRGPICKS.png",
        "authoringSource": "assets/items/pickups.blend",
        "models": models,
        "items": records,
    }
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    ZSCRIPT_PATH.write_text("\n".join(zscript), encoding="utf-8")
    MODELDEF_PATH.write_text("\n".join(modeldef), encoding="utf-8")
    print(json.dumps({"items": len(records), "models": len(list(MODEL_DIR.glob('*.obj'))), "registry": str(REGISTRY_PATH)}))


if __name__ == "__main__":
    main()
