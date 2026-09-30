# Terrain catalog assets

`tools/terrain_catalog_assets.py` creates original Project Broom low-poly
terrain meshes in `mod/BrogueDoom/models/terrain/catalog/` and the `BT*.png`
catalog surface textures it explicitly lists. These new meshes and textures
are dedicated to the public domain under CC0-1.0. No external model, image,
WAD, or downloaded asset is used to generate them.

`tools/terrain_overlays.py` also creates the original `BT*O.png` RGBA coatings
and `models/terrain/catalog/Overlay.obj` under the same CC0-1.0 dedication.
These contain no baked or sampled third-party floor textures.

`tools/terrain_debris.py` supplies the rebuilt original leaf, fungus, vine,
hide, junk and rubble meshes under the same CC0-1.0 dedication. Geometry is
procedurally authored; no external images or models are used.

The presentation-only explorer set pieces reuse the original `Bedroll`,
`Bones`, `Junk`, `FallenTorch`, `Skins`, and `Rubble` catalog meshes and the
original `BTATLAS.png` palette. They introduce no downloaded or third-party
asset and remain covered by the same CC0-1.0 dedication.

Meshes reference the new original muted palette `BTATLAS.png`, also CC0.
Existing cave, water, lava, bridge,
and other imported materials retain their existing license notices.

This is a presentation addition only. Model classes derive from the inert
terrain actor and do not collide, attack, consume turns, or run gameplay AI.
