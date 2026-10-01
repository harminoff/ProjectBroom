# Stone guardian model and animation

Presentation-only BRG-M57 / MK_GUARDIAN. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue (`Globals.c` catalog row and prose) describes a weathered stone statue of a knight carrying a battleaxe, connected to the glowing glyphs on the floor by invisible strands of enchantment. The glyph colour is white, the large flag is not set, and the source verbs are gazing and strikes. Catalog tokens include `MONST_INANIMATE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_IMMUNE_TO_FIRE`, `MONST_ALWAYS_HUNTING`, `MONST_GETS_TURN_ON_ACTIVATION`, `MONST_DIES_IF_NEGATED`, `MA_REFLECT_100`, `DF_GUARDIAN_STEP` and `DF_RUBBLE`. Brogue owns all of this: invulnerability, moving only when the player moves (turn on activation), glyph machinery, reflection, negation death, rubble, timing, AI, RNG and collision. The model adds no glow, particles, debris actors or collision.

The art is an original interpretation: a monumental sandstone knight statue from the guardian family kit. It wears an open kettle helm with a crest over a carved, stern bearded face (brow ridge, two separate shadowed eye sockets, nose, moustache and a spade beard with carved locks). It has layered pauldrons, a keeled breastplate, a carved-glyph belt and gorget, tassets and a tabard, a heavy carved cape on its own bone that keeps hanging when the body moves, and pointed sabatons. It carries a great double-bitted battleaxe in dark basalt with pale honed edges, so the weapon keeps its own silhouette against the pale body. At rest the axe stands head-down before the statue with both fists stacked on the haft, the classic vault-statue pose. The warm pale sandstone (with strong per-block value gradients) separates it from the blue-grey cobblestone walls and from the golem's grey granite. All dimensions and colours are artistic interpretation, and the geometry and textures are original Project Broom work (CC-BY-SA-4.0).

There are six cosmetic roles:

- `idle`: a statue's vigil. Only the carved head slowly sweeps its gaze.
- `advance`: a heavy planted gait, with the axe lifted off the floor and carried head-low.
- `cleave` (19 frames, key on frame 9): the axe is hauled up behind the right shoulder at t≈0.25. On the middle frame a huge overhead chop finishes low: the statue hinges forward into a wide lunge (left foot forward, right foot back, pelvis lowered by about 7.6 units) and the axe head strikes the floor far in front, to the statue's right.
- `sweep` (key on frame 9): the axe is cocked across the left hip, then swung far out to the right front at waist height, flat facing out, with the torso twisted and the stance braced wide.
- `recoil`.
- `crumble`: the knees buckle, the axe topples first, then every rigid piece settles on the floor as rubble.

Only idle and advance loop.

## Construction

- `tools/monster_models/guardian_kit.py` is the shared family kit, and it imports the golem kit read-only (`carved_block`, `stone_core`, `layout_islands`, rotations, `settle`, the golem stone pigment and corner data). It adds:
  - a rig-independent `Kit` for world-space rigid posing (`follow`, `two_bone`, `limb`, `rubble`, `collapse`);
  - `knight_specs` / `knight_parts`, a knight rig whose rest pose already grips its weapon;
  - `grip_hands`, which keeps each fist wrapped on the posed haft and allows sliding along it;
  - `hang_cape`, the per-pixel `paint` loop with a creature pigment callback, `layout_regions` for shader-keyed atlas regions, `export`, and the shared `creature_tests` base.
- `tools/monster_models/stone_guardian_animation.py` is the generator. `stone_guardian_materials.py` is the palette plus carved extras: basalt axe with honed edges, beard locks, drapery folds, and the lifted carved face. `test_stone_guardian.py` holds the tests.
- Every segment is rigid on one bone (weight 1), so there is no connected skin and no cage bake. Poses are authored at kit scale and exported uniformly at `SCALE = 0.9`.

## Delivered assets

- Runtime model: `mod/BrogueDoom/models/monsters/57_guardian.iqm`. Skin: `graphics/BRGSGRD.png`, with `_N` (flat) and `_S` maps alongside. All names were checked for collisions first: they are new, and the static `57_guardian.obj` and `BRGM57.png` are untouched.
- `assets/monsters/stone_guardian/` holds `animation.json` and `stone-guardian-animated.blend`.
- Pending row: `assets/monsters/skeletal_pending/MK_GUARDIAN.json`. Pending GLDEFS: `MK_GUARDIAN.gldefs` (normal and specular only; matte stone).
- 19 bones, 74 parts, 55,112 vertices, 27,556 triangles.
- Durations are engine tics: cleave and sweep 23, recoil 18, crumble 53.
- Across every exported frame X/Y stay within about ±31.5, with no floor compensation. The windup raise reaches 79 units; that frame is transitional, and the cleave middle frame tops out at about 54.

## Verification (phase 1)

See the hand-back for the exact export hashes, the Blender build log, the preview galleries (`artifacts/creature-queue/BRG-M57/preview-vulkan`, `preview-opengl` and their `*-contact.jpg`) and the test totals. These are phase-1 results only: integration, the packaged galleries, the native build and the shared suites belong to the coordinator gate. User art approval and the natural encounter remain open.

## Known limitations

- The windup overhead raise crosses the oblique camera's ~72-unit crop. The key frames are deliberately low and wide.
- The rigid cape cannot drape. It is counter-rotated toward hanging, and in the lunge it swings back as a stiff slab.
- The hands stay on the haft (tested), but the gauntlets are simple blocks, and the fists visibly overlap the haft.
- Rubble undersides stay painted dark because the paint uses rest-pose form light. Rubble pieces interpenetrate slightly, and no self-intersection proof is claimed.
- The helm reads as a kettle hat at close range.
