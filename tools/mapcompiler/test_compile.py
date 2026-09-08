from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from .compile import (
    ANIMATED_FLAT_BASES,
    AUTO_DESCENT,
    CHASM_FLOOR_Z,
    CHASM_LIGHT_LEVEL,
    CHASM_PORTAL_DEPTH,
    CHASM_PORTAL_SHOULDER,
    CAVE_CEILING_Z,
    CONTOUR_DEPTH,
    CONTOUR_MIN_RUN,
    CONTOUR_RUN_STRIDE,
    CONTOUR_SHOULDER,
    OPEN_VOID_CEILING_Z,
    OPEN_VOID_SKY_FLAT,
    OPEN_VOID_SKY_TEXTURE,
    PROP_RULES,
    TERRAIN_THEME_REGISTRY,
    boundary_material,
    boundary_uses_contour,
    build_material_layout,
    cell_door_is_closed,
    cell_is_solid,
    cell_has_door_geometry,
    cell_has_geometry,
    cell_is_chasm_bridge,
    cell_is_chasm_void,
    compile_package,
    contoured_side_points,
    floor_height,
    floor_material,
    edge_texture_offset,
    make_map_text,
    make_mapinfo,
    map_side_points,
    prop_placement,
    sector_ceiling,
    sector_light,
    sector_tint,
    surface_tint,
    terrain_theme,
    transition_material,
    wall_material,
)
from .verify import VerifyError, verify_map, verify_package


def sample_model() -> dict:
    cells = []
    for y in range(29):
        for x in range(79):
            dungeon = "GRANITE" if x in (0, 78) or y in (0, 28) else "FLOOR"
            cells.append(
                {
                    "x": x,
                    "y": y,
                    "layers": {
                        "dungeon": {"id": 1 if dungeon == "GRANITE" else 2, "symbol": dungeon},
                        "liquid": {"id": 0, "symbol": "NOTHING"},
                        "gas": {"id": 0, "symbol": "NOTHING"},
                        "surface": {"id": 0, "symbol": "NOTHING"},
                    },
                    "flags": 0,
                    "terrainFlags": 1 if dungeon == "GRANITE" else 0,
                    "terrainMechFlags": 0,
                    "volume": 0,
                    "machine": 0,
                    "exposedToFire": 0,
                }
            )
    return {
        "schemaVersion": 1,
        "source": {"variant": "Brogue"},
        "seed": "1",
        "dimensions": {"width": 79, "height": 29},
        "terrainCatalog": [
            {"id": 0, "symbol": "NOTHING"},
            {"id": 1, "symbol": "GRANITE"},
            {"id": 2, "symbol": "FLOOR"},
        ],
        "levels": [
            {
                "depth": 1,
                "levelSeed": "1",
                "upStairs": {"x": 1, "y": 1},
                "downStairs": {"x": 77, "y": 27},
                "cells": cells,
            }
        ],
    }


class CompilerTests(unittest.TestCase):
    def test_startup_preserves_first_map_and_all_depth_metadata(self):
        import copy
        model = sample_model()
        model['levels'].append(copy.deepcopy(model['levels'][0]))
        model['levels'][1]['depth'] = 2
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, full, startup, repeat = [root / name for name in ('input.json', 'full.pk3', 'startup.pk3', 'repeat.pk3')]
            source.write_text(json.dumps(model))
            compile_package(source, full)
            manifest = compile_package(source, startup, startup=True)
            compile_package(source, repeat, startup=True)
            self.assertEqual(startup.read_bytes(), repeat.read_bytes())
            self.assertTrue(manifest['startupOnly'])
            self.assertEqual(verify_package(source, startup, startup=True)['maps'], 1)
            with zipfile.ZipFile(full) as original, zipfile.ZipFile(startup) as prepared:
                self.assertEqual(prepared.namelist(), ['MAPINFO', 'brogue-manifest.json', 'maps/BRG01.wad'])
                self.assertEqual(prepared.read('maps/BRG01.wad'), original.read('maps/BRG01.wad'))
                self.assertEqual(prepared.read('MAPINFO'), original.read('MAPINFO'))
                entries = [(name, prepared.read(name)) for name in prepared.namelist()]
            # A missing logical depth must fail even though only floor one is built.
            with zipfile.ZipFile(startup, 'w') as damaged:
                for name, data in entries:
                    damaged.writestr(name, b'' if name == 'MAPINFO' else data)
            with self.assertRaisesRegex(VerifyError, 'depth metadata'):
                verify_package(source, startup, startup=True)

    def test_surfaces_tint_base_floor_and_bridges_replace_liquid(self) -> None:
        model = sample_model()
        cell = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))

        cell["layers"]["surface"] = {"id": 3, "symbol": "GRASS"}
        self.assertEqual(floor_material(cell), "BRGMOSS")
        self.assertNotEqual(surface_tint(cell), 0xFFFFFF)
        self.assertEqual(sector_tint(cell, "CAVE_NATURAL"), 0xFFFFFF)
        self.assertEqual(floor_height(cell), 0)

        cell["layers"]["liquid"] = {"id": 4, "symbol": "DEEP_WATER"}
        cell["layers"]["surface"] = {"id": 5, "symbol": "BRIDGE_EDGE"}
        self.assertEqual(floor_material(cell), "BRGBRID")
        self.assertEqual(terrain_theme(cell), "BRIDGE")
        self.assertEqual(floor_height(cell), 0)

        cell["layers"]["dungeon"] = {"id": 6, "symbol": "DOOR"}
        cell["terrainFlags"] = 0
        self.assertTrue(cell_is_solid(cell))
        self.assertTrue(cell_has_door_geometry(cell))
        self.assertTrue(cell_has_geometry(cell))

    def test_liquids_use_animation_bases_and_rock_boundaries(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        water = cells[(10, 10)]
        shore = cells[(11, 10)]
        water["layers"]["liquid"] = {"id": 4, "symbol": "DEEP_WATER"}

        layout = build_material_layout(cells, cells)
        self.assertEqual(terrain_theme(water, cells), "WATER")
        self.assertEqual(terrain_theme(shore, cells), "CAVE_WET")
        self.assertEqual(floor_material(water, cells=cells, layout=layout), "BRGWATR")
        self.assertEqual(floor_material(shore, cells=cells, layout=layout), "BRGEARTH")
        self.assertEqual(floor_height(water), -24)
        self.assertNotIn(
            boundary_material(water, None, cells=cells, layout=layout),
            {"WATRWAL1", "WATRWAL2", "WATRWAL3"},
        )

    def test_chasm_void_is_deep_but_safe_brink_remains_at_floor_height(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        model["terrainCatalog"].extend([
            {"id": 3, "symbol": "CHASM"},
            {"id": 4, "symbol": "CHASM_EDGE"},
        ])
        void = cells[(10, 10)]
        brink = cells[(11, 10)]
        void["layers"]["liquid"] = {"id": 3, "symbol": "CHASM"}
        void["terrainFlags"] = 1 << 7
        void["semantic"] = {"isChasm": True}
        brink["layers"]["liquid"] = {"id": 4, "symbol": "CHASM_EDGE"}
        brink["semantic"] = {"isChasm": True}

        self.assertTrue(cell_is_chasm_void(void))
        self.assertFalse(cell_is_chasm_void(brink))
        self.assertEqual(floor_height(void), CHASM_FLOOR_Z)
        self.assertEqual(CHASM_FLOOR_Z, -128)
        self.assertEqual(floor_height(brink), 0)
        layout = build_material_layout(cells, cells)
        self.assertEqual(
            sector_light(void, (10, 10), 1, cells, layout),
            CHASM_LIGHT_LEVEL,
        )
        self.assertEqual(
            boundary_material(void, cells[(10, 9)], cells=cells, layout=layout),
            "BRGCAVE",
        )

        map_text, _, _ = make_map_text(level, 79, 29)
        self.assertIn(f"heightfloor = {CHASM_FLOOR_Z};", map_text)
        self.assertIn('texturefloor = "BRGABYSS";', map_text)
        self.assertIn('texturebottom = "BRGCLIFF";', map_text)
        self.assertNotIn("texturelower =", map_text)
        self.assertNotIn("textureupper =", map_text)
        chasm_sector = next(
            block
            for block in map_text.split("sector\n")
            if "user_brogue_x = 10;" in block and "user_brogue_y = 10;" in block
        )
        self.assertIn(f"lightlevel = {CHASM_LIGHT_LEVEL};", chasm_sector)

        ground_points = map_side_points(
            29, 11, 10, 3, brink, void, cells, set(cells)
        )
        void_points = map_side_points(
            29, 10, 10, 1, void, brink, cells, set(cells)
        )
        self.assertEqual(ground_points, list(reversed(void_points)))
        self.assertEqual(len(ground_points), 4)
        straight_x = 11 * 64
        self.assertEqual(ground_points[0][0], straight_x)
        self.assertEqual(ground_points[-1][0], straight_x)
        self.assertEqual(ground_points[1][0], straight_x - CHASM_PORTAL_DEPTH)
        self.assertEqual(ground_points[2][0], straight_x - CHASM_PORTAL_DEPTH)
        self.assertEqual(abs(ground_points[1][1] - ground_points[0][1]), CHASM_PORTAL_SHOULDER)

    def test_chasm_bridge_shares_black_canopy_without_upper_wall_slab(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        model["terrainCatalog"].extend([
            {"id": 3, "symbol": "CHASM"},
            {"id": 4, "symbol": "BRIDGE_EDGE"},
        ])
        void = cells[(10, 10)]
        bridge = cells[(11, 10)]
        isolated_bridge_edge = cells[(20, 20)]
        void["layers"]["liquid"] = {"id": 3, "symbol": "CHASM"}
        void["terrainFlags"] = 1 << 7
        void["semantic"] = {"isChasm": True}
        bridge["layers"]["liquid"] = {"id": 3, "symbol": "CHASM"}
        bridge["layers"]["surface"] = {"id": 4, "symbol": "BRIDGE_EDGE"}
        bridge["semantic"] = {"isChasm": True, "isBridge": True}
        isolated_bridge_edge["layers"]["liquid"] = {"id": 3, "symbol": "CHASM_EDGE"}
        isolated_bridge_edge["layers"]["surface"] = {"id": 4, "symbol": "BRIDGE_EDGE"}
        isolated_bridge_edge["semantic"] = {"isChasm": True, "isBridge": True}

        layout = build_material_layout(cells, cells)
        self.assertTrue(cell_is_chasm_bridge(bridge, cells))
        self.assertTrue(cell_is_chasm_bridge(isolated_bridge_edge, cells))
        self.assertEqual(terrain_theme(bridge, cells), "BRIDGE")
        self.assertEqual(layout["ceiling_theme_by_position"][(10, 10)], "CAVE_NATURAL")
        self.assertEqual(layout["ceiling_theme_by_position"][(11, 10)], "CAVE_NATURAL")
        self.assertEqual(layout["ceiling_theme_by_position"][(20, 20)], "CAVE_NATURAL")
        self.assertEqual(sector_ceiling(void, (10, 10), layout), 224)
        self.assertEqual(sector_ceiling(bridge, (11, 10), layout), 224)
        self.assertEqual(
            map_side_points(29, 10, 10, 1, void, bridge, cells, set(cells)),
            contoured_side_points(29, 10, 10, 1, contoured=False),
        )

        map_text, _, stats = make_map_text(level, 79, 29)
        bridge_sector = next(
            block
            for block in map_text.split("sector\n")
            if "user_brogue_x = 11;" in block and "user_brogue_y = 10;" in block
        )
        self.assertIn("heightfloor = 0;", bridge_sector)
        self.assertIn("heightceiling = 224;", bridge_sector)
        self.assertIn('texturefloor = "BRGBRID";', bridge_sector)
        self.assertIn('textureceiling = "BRGCEIL";', bridge_sector)
        self.assertEqual(map_text.count('texturetop = "-";'), stats["sidedefCount"])

    def test_depths_below_first_use_one_open_black_sky_ceiling(self) -> None:
        model = sample_model()
        level = model["levels"][0]

        first_floor_text, _, first_stats = make_map_text(level, 79, 29)
        self.assertNotIn(f'textureceiling = "{OPEN_VOID_SKY_FLAT}";', first_floor_text)
        self.assertEqual(
            first_floor_text.count(f"heightceiling = {CAVE_CEILING_Z};"),
            first_stats["sectorCount"],
        )
        self.assertEqual(first_floor_text.count('texturetop = "-";'), first_stats["sidedefCount"])

        level["depth"] = 2
        lower_floor_text, _, lower_stats = make_map_text(level, 79, 29)
        self.assertEqual(first_stats["sectorCount"], lower_stats["sectorCount"])
        self.assertEqual(
            lower_floor_text.count(f"heightceiling = {OPEN_VOID_CEILING_Z};"),
            lower_stats["sectorCount"],
        )
        self.assertEqual(
            lower_floor_text.count(f'textureceiling = "{OPEN_VOID_SKY_FLAT}";'),
            lower_stats["sectorCount"],
        )
        self.assertNotIn('textureceiling = "BRGCEIL";', lower_floor_text)
        self.assertIn('texturemiddle = "BRGCVUP";', lower_floor_text)
        self.assertNotIn('texturemiddle = "BRGCVUP";', first_floor_text)

        mapinfo = make_mapinfo([("BRG01", 1), ("BRG02", 2)])
        first_map, second_map = mapinfo.split("map BRG02", 1)
        self.assertNotIn("sky1", first_map)
        self.assertIn(f'sky1 = "{OPEN_VOID_SKY_TEXTURE}", 0', second_map)

    def test_registry_never_assigns_non_base_animation_frames(self) -> None:
        for theme in TERRAIN_THEME_REGISTRY["themes"].values():
            for floor in theme["floors"]:
                animation_base = ANIMATED_FLAT_BASES.get(floor.lower())
                if animation_base is not None:
                    self.assertEqual(floor.lower(), animation_base)

    def test_solid_cell_boundaries_keep_full_height_wall_materials(self) -> None:
        model = sample_model()
        cell = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        cell["layers"]["dungeon"] = {"id": 1, "symbol": "GRANITE"}
        cell["terrainFlags"] = 1

        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)
        self.assertEqual(wall_material(cell), "BRGCAVE")
        self.assertIn('texturemiddle = "BRGCAVE";', map_text)
        self.assertIn("dontdraw = true;", map_text)
        self.assertIn("twosided = false;", map_text)
        self.assertIn("sideback = ", map_text)

    def test_dry_ground_above_liquid_uses_a_structural_bank(self) -> None:
        model = sample_model()
        cells = {(cell["x"], cell["y"]): cell for cell in model["levels"][0]["cells"]}
        liquid = cells[(10, 10)]
        ground = cells[(11, 10)]
        for symbol in ("DEEP_WATER", "SHALLOW_WATER", "MUD", "LAVA"):
            liquid["layers"]["liquid"] = {"id": 3, "symbol": symbol}
            layout = build_material_layout(cells, cells)
            material = transition_material(liquid, ground, "1", 1, cells, layout)
            self.assertIn(material, {"BRGCAVE", "BRGWET", "BRGMASON"}, symbol)
            self.assertNotIn(material, {"BRGWFALL", "BRGLFALL"}, symbol)

    def test_higher_liquid_surface_flows_down_the_exposed_edge(self) -> None:
        model = sample_model()
        cells = {(cell["x"], cell["y"]): cell for cell in model["levels"][0]["cells"]}
        higher = cells[(10, 10)]
        lower = cells[(11, 10)]
        for higher_symbol, lower_symbol, expected in (
            ("SHALLOW_WATER", "DEEP_WATER", "BRGWFALL"),
            ("MUD", "DEEP_WATER", "BRGSFALL"),
            ("LAVA", "DEEP_WATER", "BRGLFALL"),
        ):
            higher["layers"]["liquid"] = {"id": 3, "symbol": higher_symbol}
            lower["layers"]["liquid"] = {"id": 3, "symbol": lower_symbol}
            layout = build_material_layout(cells, cells)
            for front, back in ((higher, lower), (lower, higher)):
                self.assertEqual(
                    transition_material(front, back, "1", 1, cells, layout),
                    expected,
                    (higher_symbol, lower_symbol),
                )

    def test_liquid_over_chasm_keeps_an_animated_cliff_face(self) -> None:
        model = sample_model()
        cells = {(cell["x"], cell["y"]): cell for cell in model["levels"][0]["cells"]}
        higher = cells[(10, 10)]
        lower = cells[(11, 10)]
        lower["layers"]["liquid"] = {"id": 89, "symbol": "CHASM"}
        lower.setdefault("semantic", {})["isChasm"] = True
        lower["terrainFlags"] |= AUTO_DESCENT
        for higher_symbol, expected in (
            ("SHALLOW_WATER", "BRGWCLF"),
            ("MUD", "BRGSCLF"),
        ):
            higher["layers"]["liquid"] = {"id": 3, "symbol": higher_symbol}
            layout = build_material_layout(cells, cells)
            for front, back in ((higher, lower), (lower, higher)):
                self.assertEqual(
                    transition_material(front, back, "1", 1, cells, layout),
                    expected,
                    (higher_symbol, expected),
                )

    def test_lower_depth_boundaries_use_attached_upward_fade(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        level["depth"] = 2
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        layout = build_material_layout(cells, cells)
        self.assertEqual(
            boundary_material(cells[(10, 10)], cells[(10, 9)], "1", 2, cells, layout),
            "BRGCVUP",
        )
        map_text, _, _ = make_map_text(level, 79, 29)
        self.assertIn(f"heightceiling = {OPEN_VOID_CEILING_Z};", map_text)
        self.assertIn('texturemiddle = "BRGCVUP";', map_text)

    def test_closed_doors_receive_centered_door_faces_and_visible_markers(self) -> None:
        model = sample_model()
        door = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        door["layers"]["dungeon"] = {"id": 3, "symbol": "DOOR"}
        door["terrainFlags"] = 1

        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)

        # Door cells stay valid open volumes. A coordinate-addressable model
        # supplies the panel without creating black zero-height sectors.
        self.assertIn(f"heightfloor = 0;\n  heightceiling = {CAVE_CEILING_Z};", map_text)
        self.assertIn("id = 10800;", map_text)
        self.assertIn("user_brogue_door_sector = 1;", map_text)
        self.assertIn("type = 15020;", map_text)
        self.assertIn("arg0 = 10;\n  arg1 = 10;", map_text)
        self.assertIn("alpha = 1.000000;", map_text)
        self.assertNotIn('texturemiddle = "BRGDOOR";', map_text)
        self.assertNotIn('texturetop = "BRGDOOR";', map_text)
        self.assertNotIn('texturebottom = "BRGDOOR";', map_text)
        self.assertIn("type = 15002;", map_text)
        self.assertIn("type = 15003;", map_text)
        self.assertGreaterEqual(map_text.count("x = 96; y = 1760;"), 3)
        self.assertGreaterEqual(map_text.count("x = 4960; y = 96;"), 2)

    def test_secret_door_has_addressable_wall_camouflage(self) -> None:
        model = sample_model()
        door = next(c for c in model['levels'][0]['cells'] if (c['x'], c['y']) == (10, 10))
        door['layers']['dungeon'] = {'id': 6, 'symbol': 'SECRET_DOOR'}
        door['terrainFlags'] = 1
        first = make_map_text(model['levels'][0], 79, 29)
        self.assertEqual(first, make_map_text(model['levels'][0], 79, 29))
        self.assertIn('id = 20800; wrapmidtex = true;', first[0])
        self.assertIn('user_brogue_reveal_cell = 800;', first[0])
        self.assertIn('texturemiddle = "RRGCAVE";', first[0])
        self.assertIn('alpha = 0.000000;', first[0])
        self.assertIn('user_brogue_door_sector = 1;', first[0])

    def test_passable_brogue_door_still_starts_visually_closed(self) -> None:
        model = sample_model()
        door = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        door["layers"]["dungeon"] = {"id": 3, "symbol": "DOOR"}
        door["terrainFlags"] = 1042
        door["semantic"] = {
            "isSolid": False,
            "isWalkable": True,
            "blocksVision": True,
            "isDoor": True,
        }

        self.assertFalse(cell_is_solid(door))
        self.assertTrue(cell_has_door_geometry(door))
        self.assertTrue(cell_door_is_closed(door))

        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)
        self.assertIn(f"heightfloor = 0;\n  heightceiling = {CAVE_CEILING_Z};", map_text)
        self.assertIn("id = 10800;", map_text)

        door["layers"]["dungeon"] = {"id": 8, "symbol": "OPEN_DOOR"}
        door["semantic"]["blocksVision"] = False
        self.assertTrue(cell_has_door_geometry(door))
        self.assertFalse(cell_door_is_closed(door))

    def test_wooden_barricade_uses_distinct_authoritative_marker(self) -> None:
        model = sample_model()
        barricade = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        barricade["layers"]["dungeon"] = {"id": 20, "symbol": "WOODEN_BARRICADE"}
        barricade["terrainFlags"] = 1029
        barricade["semantic"] = {
            "isSolid": True,
            "isWalkable": False,
            "blocksVision": False,
            "isDoor": True,
        }

        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)
        self.assertTrue(cell_door_is_closed(barricade))
        self.assertIn("type = 15021;", map_text)
        self.assertIn("arg0 = 10;\n  arg1 = 10;", map_text)
        self.assertIn("alpha = 1.000000;", map_text)

    def test_wall_texture_offsets_continue_across_cell_edges(self) -> None:
        # Two horizontal 64-unit segments advance through one larger texture.
        self.assertEqual(edge_texture_offset(79, 0, 1), 0)
        self.assertEqual(edge_texture_offset(79, 1, 2), 64)
        # Vertical segments use top-to-bottom grid distance consistently.
        self.assertEqual(edge_texture_offset(79, 0, 80), 0)
        self.assertEqual(edge_texture_offset(79, 80, 160), 64)

    def test_solid_boundaries_recess_without_moving_portals(self) -> None:
        portal = contoured_side_points(29, 10, 10, 0, contoured=False)
        contour = contoured_side_points(29, 10, 10, 0, contoured=True)
        self.assertEqual(portal, [(640, 1216), (704, 1216)])
        self.assertEqual(
            contour,
            [(640, 1216), (652, 1224), (692, 1224), (704, 1216)],
        )
        self.assertEqual(CONTOUR_DEPTH, 8)
        self.assertEqual(CONTOUR_SHOULDER, 12)

    def test_contours_are_sparse_accents_on_long_wall_runs(self) -> None:
        geometry = {(x, 1) for x in range(8)}
        selected = [x for x in range(8) if boundary_uses_contour(geometry, x, 1, 0)]
        self.assertEqual(selected, [1, 5])
        self.assertEqual(CONTOUR_MIN_RUN, 3)
        self.assertEqual(CONTOUR_RUN_STRIDE, 4)
        self.assertFalse(boundary_uses_contour({(0, 1), (1, 1)}, 0, 1, 0))

    def test_props_are_deterministic_projections_of_surface_semantics(self) -> None:
        model = sample_model()
        cells = model["levels"][0]["cells"]
        placement = None
        selected_cell = None
        for cell in cells:
            if cell["x"] in (0, 78) or cell["y"] in (0, 28):
                continue
            cell["layers"]["surface"] = {"id": 3, "symbol": "GRASS"}
            placement = prop_placement(cell, "1", 1, 79, 29)
            if placement is not None:
                selected_cell = cell
                break
        self.assertIsNotNone(placement)
        self.assertEqual(placement, prop_placement(selected_cell, "1", 1, 79, 29))
        self.assertEqual(placement["type"], PROP_RULES["GRASS"][1])
        center_x = selected_cell["x"] * 64 + 32
        center_y = (29 - selected_cell["y"] - 1) * 64 + 32
        self.assertLessEqual(abs(placement["x"] - center_x), 12)
        self.assertLessEqual(abs(placement["y"] - center_y), 12)
        selected_cell["layers"]["surface"] = {"id": 0, "symbol": "NOTHING"}
        self.assertIsNone(prop_placement(selected_cell, "1", 1, 79, 29))

    def test_dense_foliage_always_receives_a_prop_and_vegetated_floor(self) -> None:
        model = sample_model()
        cell = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        cell["layers"]["surface"] = {"id": 7, "symbol": "FOLIAGE"}
        self.assertIsNotNone(prop_placement(cell, "1", 1, 79, 29))
        self.assertIsNotNone(prop_placement(cell, "999", 12, 79, 29))
        self.assertEqual(floor_material(cell), "BRGMOSS")
        map_text, _, _ = make_map_text(model["levels"][0], 79, 29, game_seed="1")
        self.assertIn('texturefloor = "BRGMOSS";', map_text)
        cell["layers"]["liquid"] = {"id": 8, "symbol": "DEEP_WATER"}
        self.assertEqual(floor_material(cell), "BRGWATR")

    def test_material_variants_are_stable_within_a_topology_region(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        geometry_cells = {position: cell for position, cell in cells.items() if not cell_is_solid(cell)}
        layout = build_material_layout(cells, geometry_cells)

        room_floors = {
            floor_material(cell, seed="1", depth=1, cells=cells, layout=layout)
            for cell in geometry_cells.values()
            if layout["space_by_position"][(cell["x"], cell["y"])] == "ROOM"
        }
        self.assertEqual(len(room_floors), 1)
        self.assertEqual(len(layout["regions"]), 1)

    def test_ordinary_room_and_corridor_cells_share_light_level(self) -> None:
        model = sample_model()
        level = model["levels"][0]
        cells = {(cell["x"], cell["y"]): cell for cell in level["cells"]}
        room_position = (10, 10)
        corridor_position = (11, 10)
        layout = {
            "theme_by_position": {
                room_position: "CAVE_NATURAL",
                corridor_position: "CAVE_NATURAL",
            },
            "space_by_position": {
                room_position: "ROOM",
                corridor_position: "CORRIDOR",
            },
        }
        room_light = sector_light(cells[room_position], room_position, 1, cells, layout)
        corridor_light = sector_light(cells[corridor_position], corridor_position, 1, cells, layout)
        self.assertEqual(room_light, 144)
        self.assertEqual(corridor_light, room_light)

    def test_package_is_deterministic_and_structurally_complete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            output_one = root / "one.pk3"
            output_two = root / "two.pk3"
            input_path.write_text(json.dumps(sample_model(), separators=(",", ":")), encoding="utf-8")

            manifest_one = compile_package(input_path, output_one)
            manifest_two = compile_package(input_path, output_two)

            self.assertEqual(output_one.read_bytes(), output_two.read_bytes())
            self.assertEqual(manifest_one, manifest_two)
            self.assertEqual(manifest_one["resourcePack"], "Project Broom Original Cave Textures")
            self.assertRegex(manifest_one["resourceSha256"], r"^[0-9a-f]{64}$")
            expected_geometry_sectors = 79 * 29 * 3
            self.assertEqual(manifest_one["maps"][0]["sectorCount"], expected_geometry_sectors)
            self.assertGreater(manifest_one["maps"][0]["vertexCount"], 0)
            self.assertEqual(manifest_one["maps"][0]["contourDepth"], CONTOUR_DEPTH)
            self.assertEqual(manifest_one["maps"][0]["contourShoulder"], CONTOUR_SHOULDER)
            self.assertGreater(manifest_one["maps"][0]["contouredBoundaryCount"], 0)
            self.assertLess(
                manifest_one["maps"][0]["contouredBoundaryCount"],
                manifest_one["maps"][0]["boundaryCount"],
            )
            self.assertGreater(manifest_one["maps"][0]["lineCount"], 0)
            self.assertGreater(manifest_one["maps"][0]["sidedefCount"], 0)
            self.assertEqual(verify_package(input_path, output_one)["maps"], 1)

            with zipfile.ZipFile(output_one) as archive:
                self.assertEqual(archive.namelist(), ["MAPINFO", "brogue-manifest.json", "maps/BRG01.wad"])
                wad = archive.read("maps/BRG01.wad")
                self.assertEqual(wad[:4], b"PWAD")
                self.assertEqual(wad[4:8], (3).to_bytes(4, "little", signed=True))

    def test_generated_grid_round_trips_without_topology_gaps(self) -> None:
        model = sample_model()
        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)
        verify_map(model["levels"][0], map_text, 79, 29)

    def test_verifier_rejects_legacy_sidedef_texture_tier_names(self) -> None:
        model = sample_model()
        map_text, _, _ = make_map_text(model["levels"][0], 79, 29)
        broken = map_text.replace("texturebottom =", "texturelower =", 1)
        with self.assertRaisesRegex(VerifyError, "nonstandard UDMF texture tier name"):
            verify_map(model["levels"][0], broken, 79, 29)

    def test_semantic_solidness_is_authoritative_when_present(self) -> None:
        model = sample_model()
        cell = next(cell for cell in model["levels"][0]["cells"] if (cell["x"], cell["y"]) == (10, 10))
        cell["terrainFlags"] = 0
        cell["semantic"] = {"isSolid": True}
        self.assertTrue(cell_is_solid(cell))
        cell["semantic"]["isSolid"] = False
        self.assertFalse(cell_is_solid(cell))


if __name__ == "__main__":
    unittest.main()
