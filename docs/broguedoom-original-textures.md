# Project Broom original cave textures

The runtime presentation no longer loads `cc4-tex.wad`. Community Chest 4 and
Sunlust remain inspection-only construction references under tooling, while
all shipped cave materials are original Project Broom assets in
`mod/BrogueDoom/graphics/`.

The compiler maps Brogue semantics through
`assets/terrain/broguedoom_cave_registry.json`. Natural cave, wet cave, worked
stone, water, sludge, lava, bridge, chasm, crypt, and machine roles resolve to
fixed `BRG*` virtual materials declared by `mod/BrogueDoom/TEXTURES.txt`.
Selection is semantic and deterministic; there is no per-cell texture lottery.

Brogue bridge cells resolve to the dedicated `BRGBRID` flat backed by
`graphics/BRGBRIDGE.png`: dark weathered timber planks with iron straps. The
worked-stone `BRGFLAG` material remains reserved for masonry, vault, crypt, and
machine roles, so bridge presentation cannot spill onto ordinary ground.

Water and lava use their generated still tiles plus GZDoom `ANIMDEFS` warp.
This is presentation only and never changes Brogue passability or simulation.
Source art is scaled to repeat every 128 world units, reducing visible seams at
the 64-unit Brogue cell boundaries.

Scaled wall materials declare `WorldPanning`, so generated sidedef offsets are
interpreted in world units and remain phase-continuous across each 64-unit map
segment. The natural-rock source is also edge-matched in both axes; panning
cannot hide a bad source-image boundary by itself.

`BRGSKY` tiles the near-black chasm artwork into a valid sky texture. Generated
maps use it through `F_SKY1` on every sector below depth 1, removing the visible
ceiling plane while leaving the first floor's continuous cave roof intact.
Every depth uses one 224-unit logical ceiling height so the
cell grid never creates freestanding upper-sidedef slabs at material borders.

The generated UDMF marks open cell-to-cell portal lines `dontdraw`. They remain
fully present for sector topology and runtime cell addressing, but the minimap
skips them and draws only meaningful cave boundaries. This avoids thousands of
per-frame line draws on Brogue's dense sector grid.
