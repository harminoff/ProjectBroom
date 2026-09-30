# Terrain prop silhouette repair

Presentation-only repair of eight models from the recent catalog pass.

| Model / terrain | Correction |
| --- | --- |
| TrampledLeaves / TRAMPLED_FOLIAGE | Green boxes replaced with pointed leaves, raised veins, broken stems and flattened paired fern leaflets. |
| TrampledFungus / TRAMPLED_FUNGUS_FOREST | Flat cylinders replaced with broken caps, visible gills and fallen stems. |
| WitheredFungus / GRAY_FUNGUS | Ball caps replaced with small damaged canopies on bent stems. |
| FungalForest / FUNGUS_FOREST | Ball caps and contrasting stick segments replaced with domed caps, pale undersides and continuous pale stems. |
| Vines / ANCIENT_SPIRIT_VINES | Bare branching rods now carry pointed leaf silhouettes. |
| Skins / MUD_DOORWAY | Rectangular hanging panels replaced with tapered necks, lobed/torn edges and folded faces. |
| Junk / JUNK | Generic boxes replaced with splintered wood and bent irregular scrap. |
| Rubble / RUBBLE | Round blobs replaced with angular stone fragments of varying sizes. |

Purpose-built hard objects such as doors, cages, altars and bedrolls retain their
appropriate structured geometry. Blood/light overlays remain unchanged. The exit
door decoration remains removed.

`tools/terrain_debris.py` creates original CC0 geometry using the existing muted
palette. Fine veins and gills use thin strips instead of expensive tubes. Each
rebuilt model stays below 2,500 triangles; the leaf patch uses 2,096. Trampled
growth stays below two world units, all geometry remains above the floor and
inside the existing tile footprint. Gameplay, placement, collisions, turns,
visibility and Brogue RNG are unchanged. This is deliberately low-poly art,
not a replacement for the game's full vegetation art style.

## Verification

- Native engine rebuilt for the additional explicit renderer gallery command.
- 38 resource/catalog/shape tests passed, including nondegenerate faces, bounds,
  grounded placement, low trampled height and deterministic generation.
- Before resources preserved in `artifacts/terrain-debris/before.pk3`.
- Nine fixed-seed gallery stages cover all eight replacements and removal.
  `brg_debris_smoke` changes only copied presentation state and checks unchanged
  authoritative hash/turn after each stage. Seed-one hash stays
  `c92268ff6250781b` at turn zero.
- Before captures: `artifacts/terrain-overlays/debris-before/`.
- Accepted captures: `debris-accepted-opengl/` and `debris-accepted-vulkan/`
  under the same directory. Vulkan loads the local validation PK3.
- The shared gameplay bridge and terrain topology did not change; gameplay and
  long-run suites were not repeated for these asset-only replacements.

Reproduce with `python -m tools.capture_terrain_overlays --debris --backend 0
--label debris-review` (one command line). The local engine receipt was refreshed
for normal launcher use. No public release or listing was changed.
