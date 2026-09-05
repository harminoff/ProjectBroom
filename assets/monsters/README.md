# Project Broom creature art

Start at the [indexed roster](../../docs/creature-model-index.md), or select a
stable `BRG-Mxx` entry in [bestiary-index.json](bestiary-index.json). There are 67
non-player kinds plus the player reference. Kind 1 is the detailed, skeletal-animated rat;
kinds 2–67 have individual static model replacements and editable Blender files
under `sources/`. The player reference is not an enemy replacement.

Each entry includes exact pinned Brogue prose, catalog colors and large flag,
source line references, horde-table membership and nominal depth expressions,
explicit inferred dimensions, source/runtime paths, geometry/skin hashes, and
separate verification state. Hordes include allies, summons and constructs, not
just hostile enemies. Do not rename Brogue's historical enum spellings.

## Sources and rebuild

- `tools/monster_models/bestiary.py`: source extraction and per-kind size/recipe
  decisions; `python -m tools.monster_models.bestiary` refreshes the index.
- `tools/monster_models/creatures.py`: original anatomical geometry and diffuse
  atlases. `python -m tools.monster_models.creatures --kind 2` rebuilds one kind;
  omit `--kind` for all 66 replacements. The existing rat is never overwritten.
- `tools/monster_models/rat_animation.py`: deterministic 28-bone rat IQM and
  six-clip animation manifest; see [the rat work report](../../docs/rat-animation-work.md).
- `tools/monster_models/generate.py`: stable class, OBJ/IQM and skin bindings; skips
  all authored geometry and fails clearly if a registered model is absent.
- `tools/monster_models/blender_creatures.py`: isolated background Blender
  source builder, with one file per creature and a separate preview collection.
  Use `-- --kind 2 --render` to build/review an individual creature, or
  `-- --render` for the whole roster. Never runs destructively in a live session.
- `tools/monster_models/verify_blender_creatures.py`: fresh-open, packed-texture,
  bounds and export-collection checks across the delivered sources.

The procedural definitions are the current reproducible master. Hand edits in
Blender must be reconciled with those definitions before regeneration. Export
only the `ASSET` collection; the 64-unit grid, 58-unit staff, floor, lights and
camera are review aids, not game geometry. `.blend` is authoring source; only the
OBJ (IQM for the rat) and PNG go into the mod package. All meshes face +X, Z up, at map-unit scale;
runtime OBJ converts `(X,Y,Z)` to `(X,Z,-Y)`.

## Provenance and licensing

Meshes and raster textures are original Project Broom assets, authored by the
Project Broom contributors with Codex-assisted procedural modeling and Blender,
under [CC-BY-SA-4.0](../../ASSETS-LICENSE.md). No external meshes, texture packs,
photographs, WAD artwork, or generated image-service artwork were imported.
Blender is a tool, not the artwork's source. Existing upstream Brogue prose and
catalog data retain their upstream licensing and attribution; see
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

These are a first static-art pass, not individually approved final sculpts or
skeletal animations. Brogue supplies no numerical physical sizes: the authored
dimensions are documented visual interpretations, not new simulation facts.
See the [rollout report](../../docs/creature-model-rollout.md) for actual proof,
limitations, and follow-up acceptance gates.
