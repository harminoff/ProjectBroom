from __future__ import annotations

from collections import Counter
import json
import re
import struct
import unittest
import zlib
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "assets" / "terrain" / "broguedoom_cave_registry.json"
GRAPHICS = ROOT / "mod" / "BrogueDoom" / "graphics"
TEXTURES = ROOT / "mod" / "BrogueDoom" / "TEXTURES.txt"
ANIMDEFS = ROOT / "mod" / "BrogueDoom" / "ANIMDEFS"
MODELDEF = ROOT / "mod" / "BrogueDoom" / "MODELDEF"
BROGUE_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue.zs"
MODELS = ROOT / "mod" / "BrogueDoom" / "models" / "stairs"
DOOR_MODEL = ROOT / "mod" / "BrogueDoom" / "models" / "doors" / "door_panel.obj"
BARRICADE_MODEL = ROOT / "mod" / "BrogueDoom" / "models" / "doors" / "wooden_barricade.obj"
PICKUP_REGISTRY = ROOT / "assets" / "items" / "brogue_pickup_registry.json"
PICKUP_MODELS = ROOT / "mod" / "BrogueDoom" / "models" / "pickups"
PICKUP_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue_pickups.zs"
PICKUP_MODELDEF = PICKUP_MODELS / "MODELDEF.txt"
ROOT_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "ZSCRIPT"
MONSTER_CATALOG = ROOT / "assets" / "monsters" / "brogue_monster_catalog.json"
MONSTER_REGISTRY = ROOT / "assets" / "monsters" / "brogue_monster_registry.json"
MONSTER_MODELS = ROOT / "mod" / "BrogueDoom" / "models" / "monsters"
MONSTER_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue_monsters.zs"
WEAPON_REGISTRY = ROOT / "assets" / "weapons" / "brogue_weapon_registry.json"
WEAPON_MODELS = ROOT / "mod" / "BrogueDoom" / "models" / "weapons"
WEAPON_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue_weapons.zs"
FX_ZSCRIPT = ROOT / "mod" / "BrogueDoom" / "brogue_fx.zs"
GLDEFS = ROOT / "mod" / "BrogueDoom" / "GLDEFS"
FRONTEND = ROOT / "src" / "gzdoom-bridge" / "brogue_bridge_frontend.cpp"


class BrogueDoomResourceTests(unittest.TestCase):
    def test_sprite_declarations_are_unique(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        sprite_names = re.findall(r'^Sprite\s+"([A-Z0-9]+)"', declarations, re.MULTILINE | re.IGNORECASE)
        counts = Counter(name.upper() for name in sprite_names)
        duplicates = sorted(name for name, count in counts.items() if count > 1)
        self.assertEqual(duplicates, [])

    def test_ground_props_do_not_reuse_structural_marker_frames(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        zscript = BROGUE_ZSCRIPT.read_text(encoding="utf-8")
        self.assertIn('Sprite "BGFUA0", 1536, 1024', declarations)
        self.assertIn('States { Spawn: BGFU A -1; Stop; }', zscript)
        self.assertIn('Sprite "BGDVA0", 1536, 1024', declarations)
        self.assertIn('States { Spawn: BGDV A -1; Stop; }', zscript)
        self.assertIn('States { Spawn: BRGF A -1; Stop; }', zscript)
        self.assertIn('States { Spawn: BRGD A -1; Stop; }', zscript)

    def test_every_model_frame_has_a_declared_fallback_sprite(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        declared_sprites = {
            name.upper()
            for name in re.findall(
                r'^Sprite\s+"([A-Z0-9]+)"',
                declarations,
                re.MULTILINE | re.IGNORECASE,
            )
        }
        modeldef = MODELDEF.read_text(encoding="utf-8")
        model_frames = re.findall(
            r'^\s*FrameIndex\s+([A-Z0-9]{4})\s+([A-Z])\b',
            modeldef,
            re.MULTILINE | re.IGNORECASE,
        )
        missing = sorted(
            f"{sprite.upper()}{frame.upper()}0"
            for sprite, frame in model_frames
            if f"{sprite.upper()}{frame.upper()}0" not in declared_sprites
        )
        self.assertEqual(missing, [])

    def test_chasm_cliff_fades_opaquely_into_abyss(self) -> None:
        data = (GRAPHICS / "BRGCLIFF.png").read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        position = 8
        compressed = bytearray()
        width = height = None
        while position < len(data):
            length = struct.unpack(">I", data[position:position + 4])[0]
            kind = data[position + 4:position + 8]
            payload = data[position + 8:position + 8 + length]
            position += 12 + length
            if kind == b"IHDR":
                width, height = struct.unpack(">II", payload[:8])
            elif kind == b"IDAT":
                compressed.extend(payload)
            elif kind == b"IEND":
                break
        self.assertEqual((width, height), (64, 128))
        raw = zlib.decompress(bytes(compressed))
        stride = 1 + width * 4
        rows = [raw[y * stride + 1:(y + 1) * stride] for y in range(height)]
        self.assertTrue(all(rows[-1][x + 3] == 255 for x in range(0, width * 4, 4)))
        self.assertTrue(all(tuple(rows[-1][x:x + 3]) == (0, 0, 0) for x in range(0, width * 4, 4)))
        upper_average = sum(rows[64][x] for x in range(0, width * 4, 4)) / width
        fringe_average = sum(rows[112][x] for x in range(0, width * 4, 4)) / width
        self.assertGreater(upper_average, fringe_average * 3)

    def test_level_transition_detaches_frontend_actors_before_map_change(self) -> None:
        frontend = FRONTEND.read_text(encoding="utf-8")
        transition = frontend[frontend.index("bool SyncLevelEvent"):frontend.index("bool EnsureStarted")]
        self.assertLess(transition.index("DetachLevelPresentation();"), transition.index("primaryLevel->ChangeLevel"))
        detach = frontend[frontend.index("void DetachLevelPresentation"):frontend.index("void BeginProjectileAnimation")]
        self.assertNotIn("->Destroy()", detach)
        command_sync = frontend[frontend.index("BrogueBridgeResult PerformCommandResult"):frontend.index("bool PerformCommand(")]
        self.assertLess(command_sync.index("if (SyncLevelEvent(result))"), command_sync.index("SyncDoorMarkers();"))
        shutdown = frontend[frontend.index("void BrogueBridge_Shutdown"):]
        self.assertIn("DetachLevelPresentation();", shutdown)
        self.assertNotIn("ClearMonsterProxies(", shutdown)

    def test_original_source_art_exists(self) -> None:
        for name in (
            "BRGROCK.png",
            "BRGDIRT.png",
            "BRGSTONE.png",
            "BRGBRIDGE.png",
            "BRGWATER.png",
            "BRGLAVA.png",
            "BRGVEG0.png",
            "BRGDOOR0.png",
            "BRGUSTA.png",
            "BRGDSTA.png",
        ):
            self.assertGreater((GRAPHICS / name).stat().st_size, 1000, name)
        self.assertGreater((GRAPHICS / "BRGPIT.png").stat().st_size, 100, "BRGPIT.png")
        self.assertGreater((GRAPHICS / "BRGCLIFF.png").stat().st_size, 100, "BRGCLIFF.png")
        self.assertGreater((GRAPHICS / "PBRSKYBL.png").stat().st_size, 100, "PBRSKYBL.png")
        self.assertGreater((GRAPHICS / "PBRCVUP.png").stat().st_size, 1000, "PBRCVUP.png")
        self.assertGreater((GRAPHICS / "PBRMSUP.png").stat().st_size, 1000, "PBRMSUP.png")
        self.assertGreater((GRAPHICS / "BRGLAVA_BM.png").stat().st_size, 1000, "BRGLAVA_BM.png")
        for prefix in ("PBWFL", "PBSFL"):
            for frame in range(8):
                name = f"{prefix}{frame:03d}.png"
                self.assertGreater((GRAPHICS / name).stat().st_size, 1000, name)
        for prefix in ("PBWCF", "PBSCF"):
            for frame in range(8):
                name = f"{prefix}{frame:03d}.png"
                self.assertGreater((GRAPHICS / name).stat().st_size, 1000, name)

    def test_open_void_walls_fade_upward_without_alpha_holes(self) -> None:
        for name in ("PBRCVUP.png", "PBRMSUP.png"):
            with Image.open(GRAPHICS / name) as image:
                image = image.convert("RGB")
                self.assertEqual(image.size, (256, 1024))
                self.assertEqual(
                    image.crop((0, 0, 256, 16)).getextrema(),
                    ((0, 0), (0, 0), (0, 0)),
                )
                top = ImageStat.Stat(image.crop((0, 0, 256, 16))).mean
                rock = ImageStat.Stat(image.crop((0, 300, 256, 500))).mean
                self.assertLess(sum(top), sum(rock) * 0.15, name)

    def test_authoritative_visual_effects_are_wired(self) -> None:
        root_zscript = ROOT_ZSCRIPT.read_text(encoding="utf-8")
        effects = FX_ZSCRIPT.read_text(encoding="utf-8")
        gldefs = GLDEFS.read_text(encoding="utf-8")
        frontend = FRONTEND.read_text(encoding="utf-8")
        header = (ROOT / "src" / "brogue-mapgen" / "src" / "brogue" / "BrogueBridge.h").read_text(encoding="utf-8")
        menu = (ROOT / "mod" / "BrogueDoom" / "MENUDEF.txt").read_text(encoding="utf-8")

        self.assertIn('#include "brogue_fx.zs"', root_zscript)
        for class_name in (
            "BrogueLavaFx", "BrogueFireFx", "BrogueGasFx", "BrogueWaterSplashFx",
            "BrogueImpactFx", "BrogueDamageFx", "BrogueDeathFx",
        ):
            self.assertIn(f"class {class_name}", effects)
        self.assertIn("A_SpawnParticle", effects)
        self.assertIn("brightmap flat BRGMOLT", gldefs)
        self.assertIn("flickerlight BROGUE_FIRE_LIGHT", gldefs)
        self.assertIn("noshadowmap 1", gldefs)
        self.assertIn("uint8_t isFire;", header)
        self.assertIn("uint8_t isGas;", header)
        self.assertIn("CVAR(Int, brg_fx_quality, 1", frontend)
        self.assertIn("void SyncCellEffects()", frontend)
        self.assertIn("void SpawnBridgeEventEffects", frontend)
        self.assertIn('Option "Effects Quality", "brg_fx_quality"', menu)

    def test_registry_assets_are_declared(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        declarations = TEXTURES.read_text(encoding="utf-8").upper()
        for theme_name, theme in registry["themes"].items():
            for name in theme["walls"] + theme["floors"] + theme["ceilings"] + [theme["door"]]:
                self.assertIn(f'"{name.upper()}"', declarations, f"{theme_name}: {name}")
            if "fall" in theme:
                self.assertIn(f'"{theme["fall"].upper()}"', declarations, f"{theme_name}: fall")

    def test_liquid_floors_warp_and_falls_animate_directionally(self) -> None:
        animdefs = ANIMDEFS.read_text(encoding="utf-8").upper()
        for name in ("BRGWATR", "BRGSLDG", "BRGMOLT", "BRGLFALL"):
            self.assertIn(name, animdefs)
        self.assertNotIn("WARP TEXTURE BRGWFALL", animdefs)
        for base, frame_prefix in (
            ("BRGWFALL", "BRGWF"),
            ("BRGSFALL", "BRGSF"),
            ("BRGWCLF", "BWCF"),
            ("BRGSCLF", "BSCF"),
        ):
            self.assertIn(f"TEXTURE {base}", animdefs)
            self.assertIn(f"PIC {base} TICS", animdefs)
            for frame in range(1, 8):
                self.assertIn(f"PIC {frame_prefix}{frame:02d} TICS", animdefs)

    def test_water_and_sludge_falls_have_distinct_downward_frames(self) -> None:
        loaded: dict[str, list[Image.Image]] = {}
        for prefix in ("PBWFL", "PBSFL"):
            loaded[prefix] = [
                Image.open(GRAPHICS / f"{prefix}{frame:03d}.png").convert("RGB")
                for frame in range(8)
            ]
            self.assertTrue(all(image.size == (256, 256) for image in loaded[prefix]))
            self.assertIsNotNone(ImageChops.difference(loaded[prefix][0], loaded[prefix][1]).getbbox())

        water_mean = ImageStat.Stat(loaded["PBWFL"][0]).mean
        sludge_mean = ImageStat.Stat(loaded["PBSFL"][0]).mean
        self.assertGreater(water_mean[2], water_mean[0] * 10)
        self.assertGreater(sludge_mean[0], sludge_mean[2] * 2)

    def test_liquid_chasm_faces_retain_rock_and_animate(self) -> None:
        cliff = Image.open(GRAPHICS / "BRGCLIFF.png").convert("RGB")
        for prefix in ("PBWCF", "PBSCF"):
            frames = [
                Image.open(GRAPHICS / f"{prefix}{frame:03d}.png").convert("RGB")
                for frame in range(8)
            ]
            self.assertTrue(all(image.size == (64, 128) for image in frames))
            self.assertIsNotNone(ImageChops.difference(frames[0], frames[1]).getbbox())
            difference = ImageChops.difference(cliff, frames[0])
            changed = sum(1 for pixel in difference.getdata() if pixel != (0, 0, 0))
            self.assertGreater(changed, 64 * 128 // 3)
            self.assertLess(changed, 64 * 128 * 9 // 10)

    def test_scaled_wall_textures_use_world_panning(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        for name in ("BRGCAVE", "BRGWET", "BRGMASON", "BRGCVUP", "BRGWTUP", "BRGMSUP", "BRGWFALL", "BRGSFALL", "BRGWCLF", "BRGSCLF", "BRGLFALL", "BRGVOID", "BRGCLIFF"):
            start = declarations.index(f'Texture "{name}"')
            end = declarations.index("}\n", start)
            self.assertIn("WorldPanning", declarations[start:end], name)
        self.assertIn('Flat "BRGABYSS", 64, 64', declarations)
        self.assertIn('Texture "BRGCLIFF", 64, 128', declarations)

    def test_subterranean_void_sky_is_declared(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        start = declarations.index('Texture "BRGSKY", 256, 128')
        end = declarations.index("}\n", start)
        sky = declarations[start:end]
        self.assertEqual(sky.count('Patch "PBRSKYBL"'), 1)
        with Image.open(GRAPHICS / "PBRSKYBL.png") as image:
            self.assertEqual(image.convert("RGB").getextrema(), ((0, 0), (0, 0), (0, 0)))

    def test_bridge_deck_has_a_dedicated_original_material(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        declarations = TEXTURES.read_text(encoding="utf-8")
        self.assertEqual(registry["themes"]["BRIDGE"]["floors"], ["BRGBRID"])
        self.assertIn('Flat "BRGBRID", 1254, 1254', declarations)
        self.assertIn('Patch "BRGBRIDGE", 0, 0', declarations)

    def test_door_and_stair_presentations_are_declared(self) -> None:
        declarations = TEXTURES.read_text(encoding="utf-8")
        self.assertIn('Texture "BRGDOOR", 574, 1180', declarations)
        self.assertIn('XScale 8.96875', declarations)
        self.assertIn('Patch "BRGDOOR0", -340, -38', declarations)
        self.assertNotIn("WorldPanning\n\tPatch \"BRGDOOR0\"", declarations)
        self.assertIn('Sprite "BRGUA0"', declarations)
        self.assertIn('Sprite "BRGNA0"', declarations)

    def test_stair_markers_use_static_obj_models(self) -> None:
        modeldef = MODELDEF.read_text(encoding="utf-8")
        zscript = BROGUE_ZSCRIPT.read_text(encoding="utf-8")
        self.assertIn("Model BrogueUpStairMarker", modeldef)
        self.assertIn('Model 0 "upstairs.obj"', modeldef)
        self.assertIn('Model 1 "up_hatch.obj"', modeldef)
        self.assertIn('Skin 1 "graphics/BRGPIT.png"', modeldef)
        self.assertIn("Model BrogueFallShaftMarker", modeldef)
        self.assertIn('Model 0 "fall_shaft.obj"', modeldef)
        self.assertIn("class BrogueFallShaftMarker : BrogueStairMarkerBase", zscript)
        self.assertIn("Model BrogueDownStairMarker", modeldef)
        self.assertIn('Model 0 "downstairs.obj"', modeldef)
        self.assertIn('Model 1 "down_void.obj"', modeldef)
        self.assertIn('Skin 1 "graphics/BRGPIT.png"', modeldef)

        expected_bounds = {
            "upstairs.obj": ((-30.0, -22.0), (0.0, 128.0), (-21.0, 21.0)),
            "up_hatch.obj": ((-31.0, 16.0), (124.0, 127.0), (-24.0, 24.0)),
            "downstairs.obj": ((-26.0, 26.0), (0.0, 7.0), (-26.0, 26.0)),
            "down_void.obj": ((-20.0, 20.0), (0.25, 0.5), (-20.0, 20.0)),
            "fall_shaft.obj": ((-30.0, 30.0), (0.0, 40.0), (-30.0, 30.0)),
        }
        for name, bounds in expected_bounds.items():
            obj = (MODELS / name).read_text(encoding="ascii")
            self.assertGreaterEqual(obj.count("\nv "), 8, name)
            self.assertGreaterEqual(obj.count("\nf "), 6, name)
            vertices = [
                tuple(float(value) for value in line.split()[1:])
                for line in obj.splitlines()
                if line.startswith("v ")
            ]
            xs, ys, zs = zip(*vertices)
            self.assertEqual((min(xs), max(xs)), bounds[0], name)
            self.assertEqual((min(ys), max(ys)), bounds[1], name)
            self.assertEqual((min(zs), max(zs)), bounds[2], name)

    def test_doors_use_bridge_controlled_presentation_model(self) -> None:
        modeldef = MODELDEF.read_text(encoding="utf-8")
        zscript = BROGUE_ZSCRIPT.read_text(encoding="utf-8")
        mapinfo = (ROOT / "mod" / "BrogueDoom" / "MAPINFO").read_text(encoding="utf-8")
        frontend = FRONTEND.read_text(encoding="utf-8")
        self.assertIn("Model BrogueDoorMarker", modeldef)
        self.assertIn('Model 0 "door_panel.obj"', modeldef)
        self.assertIn('Skin 0 "graphics/BRGDOOR0.png"', modeldef)
        self.assertIn("class BrogueDoorMarker : Actor", zscript)
        self.assertIn("15020 = BrogueDoorMarker", mapinfo)
        self.assertIn("Model BrogueBarricadeMarker", modeldef)
        self.assertIn('Model 0 "wooden_barricade.obj"', modeldef)
        self.assertIn('Skin 0 "graphics/BRGBRIDGE.png"', modeldef)
        self.assertIn("class BrogueBarricadeMarker : BrogueDoorMarker", zscript)
        self.assertIn("15021 = BrogueBarricadeMarker", mapinfo)
        self.assertIn("void SyncDoorMarkers()", frontend)
        self.assertIn("cell->isDoor && (cell->isSolid || cell->blocksVision)", frontend)
        self.assertIn("proxy.presentationType = actor->GetClass();", frontend)
        self.assertIn("if (!actor->IsA(type)) continue;", frontend)
        self.assertIn("if (actorAlive) proxy.actor->Destroy();", frontend)
        self.assertIn("Spawn(primaryLevel, type, position, NO_REPLACE)", frontend)

        obj = DOOR_MODEL.read_text(encoding="ascii")
        vertices = [
            tuple(float(value) for value in line.split()[1:])
            for line in obj.splitlines()
            if line.startswith("v ")
        ]
        xs, ys, zs = zip(*vertices)
        self.assertEqual((min(xs), max(xs)), (-2.0, 2.0))
        self.assertEqual((min(ys), max(ys)), (0.0, 124.0))
        self.assertEqual((min(zs), max(zs)), (-30.0, 30.0))

        barricade = BARRICADE_MODEL.read_text(encoding="ascii")
        barricade_vertices = [
            tuple(float(value) for value in line.split()[1:])
            for line in barricade.splitlines()
            if line.startswith("v ")
        ]
        bxs, bys, bzs = zip(*barricade_vertices)
        self.assertEqual((min(bxs), max(bxs)), (-2.0, 2.0))
        self.assertEqual((min(bys), max(bys)), (18.0, 102.0))
        self.assertEqual((min(bzs), max(bzs)), (-30.0, 30.0))

        bridge_source = (ROOT / "src" / "brogue-mapgen" / "src" / "brogue" / "BrogueBridge.c").read_text(encoding="utf-8")
        door_classifier = bridge_source[bridge_source.index("static boolean tileIsDoor"):bridge_source.index("static boolean tileIsLiquid")]
        self.assertIn("case WOODEN_BARRICADE:", door_classifier)

    def test_stair_cells_auto_travel_without_arrival_bounce(self) -> None:
        zscript = BROGUE_ZSCRIPT.read_text(encoding="utf-8")
        self.assertIn("Actor OccupyingPlayer()", zscript)
        self.assertIn("if (Armed && !WasOccupied)", zscript)
        self.assertIn("landing.Disarm();", zscript)

    def test_runtime_no_longer_loads_cc4(self) -> None:
        for relative in ("tools/mapcompiler/compile.py", "scripts/launch-seed.ps1", "scripts/launch-source-bridge.ps1"):
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("cc4-tex.wad", text, relative)
            self.assertNotIn("cc4_cave_registry", text, relative)

    def test_every_brogue_pickup_kind_has_a_model(self) -> None:
        registry = json.loads(PICKUP_REGISTRY.read_text(encoding="utf-8"))
        expected_counts = {
            1: 2, 2: 15, 4: 6, 8: 16, 16: 14, 32: 12, 64: 9,
            128: 8, 256: 12, 512: 1, 1024: 1, 2048: 1, 4096: 3,
        }
        self.assertEqual(registry["itemKindCount"], 100)
        self.assertEqual(len(registry["items"]), 100)
        self.assertEqual(
            {category: sum(item["category"] == category for item in registry["items"])
             for category in expected_counts},
            expected_counts,
        )
        self.assertEqual(
            len({(item["category"], item["kind"]) for item in registry["items"]}),
            100,
        )
        self.assertEqual(len({item["class"] for item in registry["items"]}), 100)

        for item in registry["items"]:
            model = PICKUP_MODELS / item["model"]
            obj = model.read_text(encoding="ascii")
            self.assertGreaterEqual(obj.count("\nv "), 8, item["name"])
            self.assertGreaterEqual(obj.count("\nf "), 6, item["name"])

    def test_hidden_identity_categories_have_generic_models(self) -> None:
        registry = json.loads(PICKUP_REGISTRY.read_text(encoding="utf-8"))
        hidden_categories = {8, 16, 32, 64, 128}
        self.assertEqual(
            {item["category"] for item in registry["items"] if item["identityHiddenUntilKnown"]},
            hidden_categories,
        )
        generic_models = {path.name for path in PICKUP_MODELS.glob("*_generic.obj")}
        self.assertEqual(generic_models, {
            "potion_generic.obj", "scroll_generic.obj", "staff_generic.obj",
            "wand_generic.obj", "ring_generic.obj",
        })
        modeldef = PICKUP_MODELDEF.read_text(encoding="utf-8")
        for category in hidden_categories:
            self.assertIn(f"Model BroguePickupC{category:04d}Generic", modeldef)

    def test_pickup_runtime_resources_are_wired(self) -> None:
        self.assertGreater((GRAPHICS / "BRGITEMS.png").stat().st_size, 1000)
        self.assertIn('#include "brogue_pickups.zs"', ROOT_ZSCRIPT.read_text(encoding="utf-8"))
        self.assertIn('#include "models/pickups/MODELDEF.txt"', MODELDEF.read_text(encoding="utf-8"))
        zscript = PICKUP_ZSCRIPT.read_text(encoding="utf-8")
        self.assertIn("class BroguePickupProxyBase : Actor", zscript)
        self.assertEqual(zscript.count(" : BroguePickupProxyBase {}"), 105)
        frontend = FRONTEND.read_text(encoding="utf-8")
        self.assertIn("return item.kind < 0 ? 0 : item.kind;", frontend)
        self.assertIn("if (!proxy->spawnAttempted)", frontend)

    def test_complete_brogue_monster_roster_is_generated(self) -> None:
        catalog = json.loads(MONSTER_CATALOG.read_text(encoding="utf-8"))
        registry = json.loads(MONSTER_REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(catalog["bridgeApiVersion"], 16)
        self.assertEqual(catalog["count"], 68)
        self.assertEqual(registry["nonPlayerModelCount"], 67)
        self.assertEqual(registry["presentationModelCount"], 68)
        self.assertEqual(len(registry["monsters"]), 68)
        self.assertEqual(len({entry["kind"] for entry in registry["monsters"]}), 68)
        self.assertEqual(len({entry["class"] for entry in registry["monsters"]}), 68)
        self.assertEqual(len({entry["model"] for entry in registry["monsters"]}), 68)
        for monster in registry["monsters"]:
            path=MONSTER_MODELS / monster["model"]
            if path.suffix=='.iqm':
                from tools.monster_models.iqm import inspect
                model=inspect(path.read_bytes())
                self.assertGreaterEqual(len(model['vertices']),8,monster['symbol'])
                self.assertGreaterEqual(len(model['triangles']),6,monster['symbol'])
                self.assertGreater(len(model['bones']),1)
                self.assertGreater(len(model['animations']),0)
            else:
                obj = path.read_text(encoding="ascii")
                self.assertGreaterEqual(obj.count("\nv "), 8, monster["symbol"])
                self.assertGreaterEqual(obj.count("\nf "), 6, monster["symbol"])

    def test_monster_runtime_resources_are_wired(self) -> None:
        self.assertGreater((GRAPHICS / "BRGMON.png").stat().st_size, 1000)
        self.assertIn('#include "brogue_monsters.zs"', ROOT_ZSCRIPT.read_text(encoding="utf-8"))
        self.assertIn('#include "models/monsters/MODELDEF.txt"', MODELDEF.read_text(encoding="utf-8"))
        zscript = MONSTER_ZSCRIPT.read_text(encoding="utf-8")
        self.assertIn("class BrogueMonsterProxyBase : Actor", zscript)
        self.assertEqual(zscript.count(" : BrogueMonsterProxyBase"), 68)
        self.assertNotIn("+ISMONSTER", zscript)
        frontend = FRONTEND.read_text(encoding="utf-8")
        self.assertIn("std::unordered_map<uint64_t, MonsterProxy>", frontend)
        self.assertIn("creature.presentationKind", frontend)
        self.assertIn("SyncMonsters(&result);", frontend)
        self.assertIn("MonsterAnimationsActive() || Projectile.actor", frontend)
        minimap = (ROOT / "mod" / "BrogueDoom" / "ucm" / "ucm_minimap.zsc").read_text(encoding="utf-8")
        self.assertIn('obj is "BrogueMonsterProxyBase"', minimap)
        self.assertIn("if(brogueMonster && obj.alpha <= 0) continue;", minimap)

    def test_authoritative_game_over_overlay_is_wired(self) -> None:
        frontend = FRONTEND.read_text(encoding="utf-8")
        self.assertIn("void DrawGameOverOverlay()", frontend)
        self.assertIn("State.gameResult.summary", frontend)
        self.assertIn("if (HandleGameOverInput(event)) return true;", frontend)
        self.assertIn("if (State.player.gameHasEnded)", frontend)

    def test_all_brogue_weapons_have_authoritative_viewmodels(self) -> None:
        registry = json.loads(WEAPON_REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["weaponCount"], 15)
        self.assertEqual([entry["kind"] for entry in registry["weapons"]], list(range(15)))
        self.assertEqual({entry["name"] for entry in registry["weapons"]}, {
            "dagger", "sword", "broadsword", "whip", "rapier", "flail", "mace",
            "war hammer", "spear", "war pike", "axe", "war axe", "dart",
            "incendiary dart", "javelin",
        })
        for entry in registry["weapons"]:
            obj = (WEAPON_MODELS / entry["model"]).read_text(encoding="ascii")
            self.assertGreaterEqual(obj.count("\nv "), 8, entry["name"])
            self.assertGreaterEqual(obj.count("\nf "), 6, entry["name"])

        zscript = WEAPON_ZSCRIPT.read_text(encoding="utf-8")
        self.assertEqual(zscript.count(" : BrogueVisualWeaponBase"), 15)
        self.assertIn("BridgeAttack:", zscript)
        self.assertIn("BridgeThrow:", zscript)
        self.assertNotIn("A_Fire", zscript)
        self.assertIn('#include "brogue_weapons.zs"', ROOT_ZSCRIPT.read_text(encoding="utf-8"))
        self.assertIn('#include "models/weapons/MODELDEF.txt"', MODELDEF.read_text(encoding="utf-8"))

        frontend = FRONTEND.read_text(encoding="utf-8")
        for token in ("BROGUE_COMMAND_EQUIP_ITEM", "BROGUE_COMMAND_THROW_ITEM",
                      "brogue_bridge_preview_throw", "SyncWeaponView", "KEY_MOUSE1"):
            self.assertIn(token, frontend)

    def test_bridge_driven_gui_preserves_brogue_information_boundaries(self) -> None:
        header = (ROOT / "src" / "brogue-mapgen" / "src" / "brogue" / "BrogueBridge.h").read_text(encoding="utf-8")
        adapter = (ROOT / "src" / "brogue-mapgen" / "src" / "brogue" / "BrogueBridge.c").read_text(encoding="utf-8")
        frontend = FRONTEND.read_text(encoding="utf-8")
        cvars = (ROOT / "mod" / "BrogueDoom" / "CVARINFO.txt").read_text(encoding="utf-8")
        launcher = (ROOT / "scripts" / "launch-source-bridge.ps1").read_text(encoding="utf-8")

        for token in ("inventoryLetter", "inventoryOrder", "equipmentSlot", "detailText",
                      "discovered", "currentlyVisible", "nutrition", "stealthRange"):
            self.assertIn(token, header)
        for token in ("BrogueBridgeLookResult", "BROGUE_LOOK_CREATURE",
                      "brogue_bridge_inspect_cell", "BrogueBridgeTextColorSpan",
                      "detailColorSpanCount"):
            self.assertIn(token, header)
        for token in ("itemDetails(itemDetailBuffer", "currentStealthRange()",
                      "BROGUE_COMMAND_DROP_ITEM", "ANY_KIND_OF_VISIBLE",
                      "BROGUE_COMMAND_APPLY_ITEM", "itemApplyConfirmationPrompt",
                      "describeLocation(buffer", "monsterDetails(buffer", "itemDetails(buffer",
                      "copyStyledLookText"):
            self.assertIn(token, adapter)
        for token in ("DrawStatusRail", "DrawBrogueMinimap", "DrawInventory",
                      "DrawWeaponMenu", "WrapTextPixels", "HandleInventoryInput",
                      "DrawLookOverlay", "RefreshLook", "CycleLookTarget",
                      "WrapTextRanges", "DrawStyledLookText", "LookSpanColor",
                      "BROGUE_ITEM_ACTION_UNEQUIP", "BROGUE_ITEM_ACTION_APPLY",
                      "DrawApplyOverlay", "SubmitApply", "Enter/U Use",
                      "DrawCommandConfirmationOverlay", "SubmitConfirmableCommand",
                      "Damage %d-%d", "L Look"):
            self.assertIn(token, frontend)
        look_overlay = frontend[frontend.index("void DrawLookOverlay"):frontend.index("CCMD(brg_wait)")]
        self.assertIn("hasBrogueDetail", look_overlay)
        self.assertNotIn("LookResult.summary,\n\t\twidth - inset * 2, rowStep, 2", look_overlay)
        action_mapper = frontend[frontend.index("bool MapKeyToAction"):frontend.index("void ClearTargetMarkers")]
        self.assertIn("case KEY_SPACE", action_mapper)
        self.assertNotIn("case 0x4c", action_mapper)
        self.assertNotIn("case 0x48", action_mapper)
        self.assertIn("Space Wait", frontend)
        self.assertNotIn("Numpad 8-way / 5 Wait", frontend)
        self.assertIn("CVAR(Bool, brg_debug, false", frontend)
        self.assertIn("if (brg_debug)", frontend)
        self.assertIn('"+set", "brg_debug", "false"', launcher)
        self.assertIn("frameX + frameWidth - frame", frontend)
        self.assertIn("Arrows/Wheel Select", frontend)
        self.assertIn("ucm_mapshowall = false", cvars)
        self.assertIn('\"+ucm_mapshowall\", \"false\"', launcher)

    def test_executable_startup_prepares_random_seed_then_opens_brogue_menu(self) -> None:
        mapinfo = (ROOT / "mod" / "BrogueDoom" / "MAPINFO").read_text(encoding="utf-8")
        menudef = (ROOT / "mod" / "BrogueDoom" / "MENUDEF.txt").read_text(encoding="utf-8")
        gameinfo = (ROOT / "mod" / "BrogueDoom" / "GAMEINFO").read_text(encoding="utf-8")
        launcher = (ROOT / "scripts" / "launch-source-bridge.ps1").read_text(encoding="utf-8")
        engine_patch = (ROOT / "patches" / "uzdoom-project-broom.patch").read_text(encoding="utf-8")
        launcher_source = (ROOT / "tools" / "BrogueDoomLauncher" / "Program.cs").read_text(encoding="utf-8")

        for token in ("ClearEpisodes", "Episode BRG01", "NoSkillMenu", 'TitlePage = "TITLEPIC"',
                      "TitleTime = 86400", "PageTime = 86400"):
            self.assertIn(token, mapinfo)
        self.assertTrue((ROOT / "mod" / "BrogueDoom" / "graphics" / "TITLEPIC.png").is_file())
        for token in ('ListMenu "MainMenu"', "Size 640, 400", 'Font "BrogueMenu", "Untranslated", "Gold"',
                      'TextItem "NEW GAME"',
                      '"PlayerclassMenu"', 'TextItem "OPTIONS"', 'TextItem "QUIT"'):
            self.assertIn(token, menudef)
        self.assertNotIn('TextItem "LOAD GAME"', menudef)
        for token in ("[switch]$RandomSeed", "RandomNumberGenerator", "--export-dungeon-json",
                      "Get-BrogueSha256", "Copy-BrogueFileIfDifferent", 'if ($Menu)', '"+menu_main"'):
            self.assertIn(token, launcher)
        self.assertNotIn("Get-FileHash", launcher)
        self.assertIn("BrogueBridge_Shutdown();", engine_patch)
        self.assertIn('STARTUPTITLE = "Project Broom"', gameinfo)
        self.assertIn('"PROJECT BROOM"', menudef)
        self.assertIn('"BROGUE CE IN 3D"', menudef)
        self.assertIn('Text = "Project Broom"', launcher_source)
        self.assertIn('Text = "PROJECT BROOM"', launcher_source)
        self.assertNotIn("Freedoom", gameinfo)
        fontdefs = (ROOT / "mod" / "BrogueDoom" / "FONTDEFS").read_text(encoding="utf-8")
        self.assertIn("BrogueMenu", fontdefs)
        self.assertIn('TEMPLATE "BFT%03d"', fontdefs)
        self.assertEqual(94, len(list((ROOT / "mod" / "BrogueDoom" / "graphics" / "fonts" / "menu").glob("BFT*.png"))))
        for token in ("-RandomSeed", "-Menu", "--seed", "FindProjectRoot",
                      "launcher-last.log", "ProgressBarStyle.Marquee", "UpdateProgress",
                      "GENERATING THE DUNGEON", "BUILDING THE 3D CAMPAIGN",
                      "VERIFYING THE CAMPAIGN", "CreateNoWindow = true"):
            self.assertIn(token, launcher_source)
        for token in ("Using cached Brogue dungeon", "Using cached UZDoom campaign",
                      "Verifying map topology", "Launching UZDoom"):
            self.assertIn(token, launcher)

    def test_side_by_side_comparison_mode_is_exact_commit_and_edge_driven(self) -> None:
        frontend = FRONTEND.read_text(encoding="utf-8")
        source_launcher = (ROOT / "scripts" / "launch-source-bridge.ps1").read_text(encoding="utf-8")
        comparison_launcher = (ROOT / "scripts" / "launch-comparison.ps1").read_text(encoding="utf-8")
        comparison_doc = (ROOT / "docs" / "brogue-gzdoom-comparison-mode.md").read_text(encoding="utf-8")

        for token in (
            "brg_compare_pid", "GetAsyncKeyState", "ComparisonKeysDown",
            "DeliverComparisonKey", 'PerformAction(ComparisonKeys[index].action, "comparison-numpad")',
            "VK_NUMPAD8", "VK_NUMPAD9", "VK_NUMPAD6", "VK_NUMPAD3",
            "VK_NUMPAD2", "VK_NUMPAD1", "VK_NUMPAD4", "VK_NUMPAD7", "VK_NUMPAD5",
        ):
            self.assertIn(token, frontend)
        for token in ("ComparePid", "WindowWidth", "WindowHeight", "HudScale", "PassThru", '"brg_compare_pid"', '"brg_hud_scale"'):
            self.assertIn(token, source_launcher)
        for token in (
            "source-7f52dd9", 'ArgumentList @("--seed", $Seed)', "SetWindowPos",
            "ComparePid $brogue.Id", "HudScale $HudScale", "Get-FileHash", "fedacd18f475a2f9c702166b2b3193371e0498953675826b74ba53b019d9512b",
        ):
            self.assertIn(token, comparison_launcher)
        self.assertIn("two independent simulations", comparison_doc)
        self.assertIn("neither process copies coordinates", comparison_doc)

    def test_bridge_hud_has_coherent_adjustable_scaling(self) -> None:
        frontend = FRONTEND.read_text(encoding="utf-8")
        for token in (
            "brg_hud_scale", "double HudScale()", "int HudSize(int value)",
            "int StatusRailWidth()", 'V_GetFont("BrogueUI")',
            'font->StringWidth("Nutrition   0000 / 0000")',
            "void HudRailText", "DTA_ClipRight, StatusRailWidth()",
            'V_GetFont("BrogueMap")', "DTA_ScaleX, HudScale()",
            "DTA_BilinearFilter, false", "DTA_FillColor, HudColor(color)",
            "DTA_FillColor, foreground", "const int cellWidth = 5",
            "const int cellHeight = 8", "const int rowStep = HudSize(23)",
            "const int footerHeight = HudSize(28)", "cell.displayCodepoint",
            "cell.foregroundRed", "cell.backgroundRed", "DrawChar(twod, font",
        ):
            self.assertIn(token, frontend)

        fontdefs = (ROOT / "mod" / "BrogueDoom" / "FONTDEFS").read_text(encoding="utf-8")
        self.assertIn("BrogueUI", fontdefs)
        self.assertIn('TEMPLATE "BFU%03d"', fontdefs)
        self.assertIn("BrogueMap", fontdefs)
        self.assertIn('TEMPLATE "BFM%03d"', fontdefs)
        for directory, prefix, expected_size in (("ui", "BFU", (12, 22)), ("map", "BFM", (5, 8))):
            glyphs = sorted((ROOT / "mod" / "BrogueDoom" / "graphics" / "fonts" / directory).glob(f"{prefix}*.png"))
            self.assertEqual(94, len(glyphs))
            data = glyphs[0].read_bytes()
            self.assertEqual(b"\x89PNG\r\n\x1a\n", data[:8])
            self.assertEqual(expected_size, tuple(int.from_bytes(data[offset:offset + 4], "big") for offset in (16, 20)))

        bridge = (ROOT / "src" / "brogue-mapgen" / "src" / "brogue" / "BrogueBridge.c").read_text(encoding="utf-8")
        self.assertIn("copyPlainText(outState->messages", bridge)


if __name__ == "__main__":
    unittest.main()
