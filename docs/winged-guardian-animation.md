# Winged guardian model and animation

Presentation-only BRG-M58 / MK_WINGED_GUARDIAN. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue describes a statue of a sword-wielding angel that surveys the room, connected to the glowing glyphs on the floor by invisible strands of enchantment. The glyph colour is blue, the large flag is not set, and the verbs are gazing and strikes. Catalog tokens include `BOLT_BLINKING`, `DF_SILENT_GLYPH_GLOW`, `DF_RUBBLE`, `MA_REFLECT_100`, `MONST_INANIMATE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_GETS_TURN_ON_ACTIVATION` and `MONST_DIES_IF_NEGATED`. Brogue owns the blink relocation, invulnerability, glyph machinery, reflection, negation death, rubble, timing, AI and RNG. The wings are carved stone and never fly. There is no glow, blink effect, particles or collision.

The art is an original interpretation from the stone guardian's lineage, built on the same shared knight kit. It is a cool white statuary marble angel with blue-grey veining, and the Brogue blue appears only as vein and blade tint, never as glow. Its features:

- a serene carved face (brow, shallow eye sockets, nose and chin) under a carved glyph circlet, with carved hair and side locks, and no helm;
- a lighter plate harness with smaller pauldrons;
- a split robe whose panels ride each thigh, so a stride parts the skirt;
- a blue-grey polished stone longsword with a dark fuller and bright edges, held two-handed at guard with the tip beside the right shoulder;
- two carved stone wings on two bones each: a leading-edge bar, three covert rows and seven flight feathers with carved shaft and barb lines. At rest they fold behind the shoulders.

The whole statue is far brighter than the cobblestone walls, and the marble and sword make it clearly distinct from the sandstone stone guardian and the grey golem.

Roles:

- `idle`: the head surveys the room and the wings barely settle.
- `stride`: a stately planted step with the wings half open.
- `thrust` (key on frame 9): drawn back at t≈0.25, then a deep lunging stab driven forward and down while both wings flare into a wide heraldic V that reaches the cell sides (about ±30 units) below the camera crop.
- `slash` (key on frame 9): raised high on the left, then a low, wide cut finished out to the right with the torso twisted and both wings swept back.
- `recoil`: the wings flinch forward.
- `crumble`: the knees buckle, the wings break off first and lie flat behind, and the statue settles as rubble with the sword on the floor.

## Construction

- The generator is `tools/monster_models/winged_guardian_animation.py`. It uses the shared `guardian_kit` knight with the head, cape and tassets disabled, and adds its own head, robe, wings and sword.
- `winged_guardian_materials.py` covers the marble veins, sword, feather vanes, hair locks and robe folds on the golem stone pigment.
- The tests are in `test_winged_guardian.py`.
- Every segment is rigid, with no connected skin and no cage bake. The export scale is `SCALE = 0.9`.

## Delivered assets

- Runtime model: `mod/BrogueDoom/models/monsters/58_winged_guardian.iqm`. Skin: `graphics/BRGWGRD.png`, with the `_N` (flat) and `_S` maps alongside. The names are new and collision-checked; the static OBJ and `BRGM58.png` are untouched.
- `assets/monsters/winged_guardian/` holds `animation.json` and `winged-guardian-animated.blend`.
- The pending files are `MK_WINGED_GUARDIAN.json` and `MK_WINGED_GUARDIAN.gldefs` (normal and specular only).
- 26 bones (each wing: arm, hand, mid and tip), 155 parts, 124,800 vertices and 62,400 triangles.
- Durations are thrust/slash 23, recoil 18 and crumble 53 tics.
- X/Y stay within about ±31.5 in every frame, with no floor compensation. The only frames above 66 units are the transitional slash raise.

## Verification (phase 1)

See the hand-back for the hashes, the Blender log, the galleries (`artifacts/creature-queue/BRG-M58/preview-vulkan`, `preview-opengl` and the `*-contact.jpg` sheets) and the test totals. These are phase-1 results only. User art approval and the natural encounter remain open.

## Rework history

- **Round 1:** folded wings on two rigid bones each, a small face and a cap-like hair mass. From the gameplay camera it read as the stone guardian holding a sword.
- **Round 2 (coordinator rework):**
  - The wings are now carried half raised. The wrist arch rises about 7 units above the head and the feather tips flare about 10 units past the pauldrons in the front view, still inside the cell and below the oblique crop.
  - Each wing gained a `mid` and a `tip` bone under the hand. The eight flight feathers are split across three bones (tip 0-2, mid 3-4, hand 5-7), so the primaries fan in the thrust and slash instead of moving as one slab.
  - The face is larger, with a lidded eye, brow, nose bridge, upper and lower lips, cheeks and chin. The hair is a crown with three carved locks down each side and four down the back.
  - The feather paint gained a value range: dark gaps at the vane edges and roots, shaded undersides and alternate feathers a step darker.
  - The palette is unchanged, so it stays distinct from the stone guardian.
- **Round 3 (coordinator rework):** round 2 still read as two bare arms with knobs and hanging feathers.
  - The bare wing bar, scapula and wrist knuckle are gone. The leading edge is now a quadratic arc from the shoulder up over the head line and down to the wrist, covered by three overlapping rows of scalloped coverts (11, 10 and 9 per wing), so the wrist is a smooth feathered bend.
  - Eight long flight feathers start along the lower leading edge and fan to the tips, which flare about 27 units out in the rest pose.
  - The rest of the wing is unchanged: arm, hand, mid and tip bones, with the same fan in thrust and slash.
  - The head is rounder, with a softer brow, and the side locks now fall over the shoulders.
  - The feather paint no longer lets ambient occlusion crush the dense vanes to black.
- **Round 4 (coordinator authority fix):** Brogue colours the winged guardian blue and the stone guardian white. The marble is now a cool steel-blue stone with near-white cool highlights, deep saturated lapis veins and deep slate-blue gaps between feather vanes. It is still plain stone, with no glow. Geometry is unchanged, so the IQM hash is unchanged. A hue test checks that the lit stone is blue (measured hue about 216 degrees) and differs from the stone guardian's warm sandstone.

## Known limitations

- The hair is darker than the face, but it can still read as a hood at 128 units.
- The wings are tall and fairly narrow from the front, because the arc rises steeply.
- The fan is modest (the tip group rotates 14 degrees about the wrist) so the wings stay inside +/-32.
- Rubble undersides are painted dark, and pieces interpenetrate slightly.
