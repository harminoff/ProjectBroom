# Terrain overlay audit

Implemented after this audit: see [rendering changes and verification](terrain-overlay-implementation.md).

Audited 2026-09-09: all 27 new generated surface families (35 tile bindings),
their generator, Brogue layer projection, settled renderer, shoreline refresh,
and representative new surface props. Source and generated-image inspection only;
no renderer changes or new runtime captures were made.

The supplied screenshot selects **SUNLIGHT_POOL**, described as "a patch of
sunlight". Blood has the same underlying presentation defect.

## Confirmed cause

Every generated catalog surface PNG is RGB, with no transparency. In
`tools/terrain_catalog_assets.py`, puddle, lichen, dust, and light treatments paste
colored islands onto an invented brown soil background. Glyphs instead have a
solid dark background. These backgrounds do not preserve the existing floor.

`appearanceAddTile()` projects ordinary non-dungeon terrain into a single
`ground` field. `ApplyTerrainCell()` selects that field's floor material ahead of
the underlying `structure` material. `UpdateShorelines()` repeats this choice.
Consequently the effect replaces the whole floor tile; this is not merely a
texture-edge problem. Changing PNGs to RGBA alone would not establish a separate
underlying rendered floor.

## Bindings requiring overlay or substrate-preserving treatment

| Tiles | Required presentation |
| --- | --- |
| RED_BLOOD, GREEN_BLOOD, PURPLE_BLOOD | Irregular blood over the actual floor, with no replacement soil surround. |
| ACID_SPLATTER, VOMIT, URINE, WORM_BLOOD, PUDDLE, ECTOPLASM | Localized residue, viscera, or liquid patches over the substrate; retain exposed floor between patches. |
| ASH, EMBERS | Scattered ash/embers over the floor; coverage can obscure parts without replacing the surrounding material. |
| LICHEN, HAY | Growth or piled material over the substrate. Dense coverage is reasonable, but exposed areas must retain the underlying floor. |
| SUNLIGHT_POOL, DARKNESS_PATCH, PORTAL_LIGHT, GUARDIAN_GLOW | Lighting/shading effects that retain floor detail, rather than opaque colored islands on new soil. |
| MACHINE_GLYPH, MACHINE_GLYPH_INACTIVE, SACRED_GLYPH | Engraved/glowing marks over the floor, without a dark square background. |
| MACHINE_COLLAPSE_EDGE_SPREADING | Cracks on the existing ground, preserving its material until Brogue changes its state. |
| HOLE_EDGE | Translucent-ground treatment; the current opaque marble-like texture does not communicate its description. This needs a dedicated treatment, not an ordinary stain. |

This accounts for **22 tile bindings**. Layer enum alone is insufficient to
classify them: sunlight/shadows occupy Brogue's LIQUID layer, machine glyphs can
occupy DUNGEON, and blood occupies SURFACE. Their descriptions and authoritative
state must also guide presentation.

## Actual materials and structures

The remaining 13 bindings can legitimately cover or replace a material:
CARPET, BURNED_CARPET, MARBLE_FLOOR, STONE_BRIDGE,
CHASM_WITH_HIDDEN_BRIDGE_ACTIVE, OBSIDIAN, ACTIVE_BRIMSTONE, INERT_BRIMSTONE,
LAVA_RETRACTING, MUD_FLOOR, CRYSTAL_WALL, FORCEFIELD, and FORCEFIELD_MELT.
This classification does not certify their visual quality: forcefields and molten
or cooling surfaces still need their own appropriate effects. Burned carpet
should retain a carpet substrate, not be treated as generic ash.

## Surface props have a related substrate problem

Bones, rubble, junk, broken glass, webs, and netting already have separate model
geometry. However their bindings specify BRGEARTH, and the same `ground` priority
can replace carpet or marble beneath them with earth. Trampled foliage and
trampled fungus similarly select BRGMOSS. Separate prop geometry therefore does
not, by itself, prove correct floor preservation.

There is also only one ordinary `ground` slot in the appearance projection:
later layers can overwrite earlier non-liquid ground effects. A future fix must
address coexistence, not only the appearance of individual gallery tiles.

## Correction and acceptance requirements

- Separate the substrate material from surface coatings, props, and lighting.
  Keep Brogue authoritative; do not infer unobserved layers from nearby cells.
- Render stains/glyphs as separate masked geometry or a composited material that
  retains the actual substrate. Preserve texture scale and avoid z-fighting.
- Treat sunlight and shadows as floor-preserving illumination/shading, and
  HOLE_EDGE as the described translucent transition.
- Ensure settled updates, shoreline refresh, animation, and disappearance all
  restore the correct substrate. Preserve knowledge-safe remembered terrain.
- Verify stains, glyphs, light, and debris on earth, marble, carpet, and bridges
  wherever those combinations occur in authoritative state; verify liquid
  interaction and effect coexistence without adding new gameplay combinations.
- Capture fixed-seed before/after views and check deterministic state/geometry,
  visibility, transitions, and removal. The earlier single-tile terrain gallery
  is insufficient evidence for correct layering.

## Evidence locations

- `tools/terrain_catalog_assets.py`: SURFACES and surface().
- `assets/terrain/terrain_presentation.json`: floor and actor bindings.
- `mod/BrogueDoom/graphics/BT*.png`: generated opaque RGB surfaces.
- `src/brogue-mapgen/src/brogue/Globals.c`: descriptions and feature layers.
- `src/brogue-mapgen/src/brogue/BridgeTerrainAppearance.inc`: appearanceAddTile().
- `src/gzdoom-bridge/brogue_terrain_frontend.inc`: ApplyTerrainCell() and props.
- `src/gzdoom-bridge/brogue_shoreline_frontend.inc`: UpdateShorelines().

This audit qualifies the earlier terrain-description audit: a matching material
name or silhouette is not sufficient when it replaces the wrong underlying layer.
