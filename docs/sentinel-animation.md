# Sentinel model and animation

Presentation-only BRG-M37 / MK_SENTINEL. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue describes an ancient statue of an unrecognizable humanoid figure holding aloft a crystal that gleams with ancient warding magic. Sentinels are always found in groups, and each repairs damage done to the others. The glyph colour is `sentinelColor` (3, 3, 30), the light is `SENTINEL_LIGHT` (`sentinelLightColor` 20, 20, 120), and the verbs are focusing and hits. Its tokens are `MONST_TURRET`, `MONST_CAST_SPELLS_SLOWLY`, `MONST_DIES_IF_NEGATED`, `BOLT_HEALING`, `BOLT_SPARK` and `DF_RUBBLE_BLOOD`. Brogue owns its immobility, slow casting, spark and healing bolts, group behaviour, light, negation death, rubble, timing, AI and RNG. The model never leaves its plinth: the walk role is a static rest, and unused locomotion is absent. Only the crystal is fullbright, through an atlas-keyed shader, with no dynamic light, projectile, particles or collision.

The art is an original interpretation. It is a weathered indigo-slate statue on a stepped, chipped plinth:

- a flared robed column with an incised glyph band;
- a narrow torso with a glyph-carved mantle and collar;
- a faceless, eroded ovoid head tilted up toward the crystal ("unrecognizable");
- sleeved arms raised to cradle a faceted blue bipyramid crystal above the head, with two smaller side crystals;
- five small crystal shards orbiting the crystal.

The indigo hue and pale worn edges separate the stone from the neutral cobblestone walls, and the bright blue crystal is the read at distance. It stays clearly distinct from the three knights: smaller, faceless, on a plinth, and glowing.

Roles:

- `idle`: the crystal turns and bobs while the shards orbit.
- `rest`: the walk role, the same motion at a gentler bob; immobile.
- `focus` (key on frame 9): a casting pulse. The crystal is gathered to the chest at t≈0.25. On the middle frame it is thrust forward at arm's length while the shards blaze outward into a wide ring (radius about 16) facing the target and the figure leans back.
- `mend` (key on frame 9): the crystal is lowered into cupped hands before the chest, the head bows, and the shards spread into a wide, low horizontal ring around the figure.
- `jolt`: the hit reaction, with the body and crystal shuddering and shards jittering.
- `shatter`: the crystal cracks loose first and its shards scatter and fall; then the statue breaks at the waist and topples into rubble beside its plinth.

## Construction

- The generator is `tools/monster_models/sentinel_animation.py`, which has its own rig and uses the `guardian_kit` posing, painting and `layout_regions`.
- Stone islands are packed into the atlas square (0, 512, 1536). Crystal and shard islands live only in `GLOW_REGION` (1536, 0, 512).
- `mod/BrogueDoom/shaders/sentinel-crystal.fp` makes exactly the texels with u ≥ 0.75 and v < 0.25 fullbright, with a slow shimmer. The unit tests verify that each island lies inside that region exactly when it is crystal.
- `sentinel_materials.py` paints indigo stone on the golem pigment plus faceted crystal colour.
- The tests are in `test_sentinel.py`.
- Every segment is rigid, with no connected skin and no cage bake. The export scale is 0.94.

## Delivered assets

- Runtime model: `mod/BrogueDoom/models/monsters/37_sentinel.iqm`. Skin: `graphics/BRGSNTL.png`. The shader is new, and all names were checked for collisions; the static OBJ and `BRGM37.png` are untouched.
- `assets/monsters/sentinel/` holds `animation.json` and `sentinel-animated.blend`.
- The pending files are `MK_SENTINEL.json` (the shader is in `ownedFiles`) and `MK_SENTINEL.gldefs` (shader only).
- 16 bones, 29 parts, 23,752 vertices and 11,876 triangles.
- The root and plinth never move (tested).
- X/Y stay within about ±26.5 in every frame, with a maximum height of about 62.

## Verification (phase 1)

See the hand-back for the hashes, the Blender log, the galleries (`artifacts/creature-queue/BRG-M37/preview-*`) and the test totals. The crystal shader's shimmer uses renderer time, so the gallery hashes never repeat; key frames were checked visually. These are phase-1 results only. User art approval and the natural encounter remain open.

## Known limitations

- The shards and crystal are small at 192 units; the pulse reads mainly through the moved crystal and the spread of blue points.
- The shatter scatters rigid shards and crystal; the crystal does not fracture into more pieces.
- The stone is dark by design (the source colour is a deep blue). The pale worn edges carry the silhouette, but it is lower contrast than the knights.
- Rubble undersides are painted dark, and rubble interpenetrates slightly.
