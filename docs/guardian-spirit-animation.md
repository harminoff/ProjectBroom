# Guardian spirit model and animation

Presentation-only BRG-M59 / MK_CHARM_GUARDIAN. Brogue CE remains authoritative.

## Source facts, art and planned proof

Pinned Brogue describes a spectral outline of a knight carrying a battleaxe that casts an ethereal light on its surroundings. The glyph colour is `spectralImageColor`, a flickering red, and the monster carries `SPECTRAL_IMAGE_LIGHT`. Its tokens are `MA_REFLECT_100`, `MONST_INANIMATE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_IMMUNE_TO_FIRE`, `MONST_DIES_IF_NEGATED`, `MONST_ALWAYS_USE_ABILITY` and `MONST_NEVER_SLEEPS`. Brogue summons it through the guardian charm and owns its allegiance, invulnerability, reflection, negation death, timing, every strike and the light it casts. This model is only additive crimson geometry. It adds no dynamic light, particles or collision.

The art is an original interpretation that shares the guardian family's knight kit, so it has the same subject as the stone guardian (a knight with a battleaxe). It is drawn as warm gold-white light rather than stone, which gives the allied spirit a benevolent but powerful read that is clearly not hostile stone and not a violet or blue phantom. Brogue's red appears only as a faint rose warmth in the dimmest interiors. Its features:

- a closed great helm with a crest and a bright cross-shaped visor slit;
- smooth, unchipped plate;
- a cloak and tapered greaves that fade away below the knee, so there are no feet;
- a single great bearded crescent battleaxe held at port across the body.

It hovers 4 units above the floor. The paint is authored for additive rendering, where black is empty: a dim crimson core with pink-white plate edges (the spectral sword palette). The shader adds a view-dependent rim and a slow renderer-time shimmer.

Roles:

- `idle`: a weightless bob with the cloak drifting.
- `glide`: leaning forward, legs trailing and cloak streaming.
- `reap` (key on frame 9): raised over the right shoulder, then a great diagonal reaping cut that finishes low and wide on the spirit's left, body swept and twisted.
- `jab` (key on frame 9): drawn back, then a lunge driving the axe's top spike straight out ahead at chest height with the haft level.
- `recoil`.
- `fade`: the light gives out, the empty armour sags, then clatters to the floor as a pile.

## Construction

- The generator is `tools/monster_models/guardian_spirit_animation.py`, built on `guardian_kit` with the greathelm head, tapered legs and a smooth finish.
- `guardian_spirit_materials.py` paints the luminous layer.
- The shader is `mod/BrogueDoom/shaders/guardian-spirit-glow.fp`: fullbright, rim and shimmer, mesh-local only.
- The tests are in `test_guardian_spirit.py`.
- The profile sets `emissive` and `additiveFlame`, and lists the shader in `ownedFiles`. There are no `_N`/`_S` maps because the material is shader-only.
- Every segment is rigid, with no connected skin and no cage bake.

## Delivered assets

- Runtime model: `mod/BrogueDoom/models/monsters/59_charm_guardian.iqm`. Skin: `graphics/BRGGSPR.png`. The shader is new. All names were checked for collisions.
- `assets/monsters/guardian_spirit/` holds `animation.json` and `guardian-spirit-animated.blend`.
- The pending files are `MK_CHARM_GUARDIAN.json` and `MK_CHARM_GUARDIAN.gldefs`.
- 19 bones, 46 parts, 34,688 vertices and 17,344 triangles.
- The leg end bones carry no geometry: the greaves taper out.
- X/Y stay within about ±30.5, and the spirit hovers above 4.5 units in every frame except the fade.

## Verification (phase 1)

See the hand-back for the hashes, the Blender log, the galleries (`artifacts/creature-queue/BRG-M59/preview-*`) and the test totals. The shader animates with renderer time, so every capture differs by a few pixels and the gallery hash check cannot detect a frozen capture on its own. The key frames were therefore compared visually. These are phase-1 results only. User art approval and the natural encounter remain open.

## Rework history

- **Round 1:** the family's knight kit with the chip and roughness turned off. It read as stacked rounded boxes, and additive overlap made the interior busy.
- **Round 2 (coordinator rework):**
  - The armour is now `spirit_armour()` in `guardian_spirit_animation.py`: a cuirass tapering to the waist with a forward keel, a gorget cone, domed pauldrons, cylindrical limb sleeves, overlapping faulds and tapered greaves. It no longer calls the knight kit.
  - Interior plates that only stacked light are gone: the hip block, lower lame, tabard, buckle, tassets and second backplate.
  - The shader draws faces turned away from the camera as nothing, so back plates add no light.
  - The glow is strongest at the rim with a dim core: `(0.22 + 1.7 * rim)`.
  - Light near the floor dims by world height (0.4 at floor level, full above 14 units), so the collapsed armour of the fade glows dimly. This assumes the floor is near world z = 0; the fixture and ordinary Brogue floors are.
  - The palette, the axe and the key poses are unchanged.
- **Round 3 (coordinator rework):** round 2 still read as stacked translucent capsules with piled light.
  - (superseded in round 4) The spirit is now rendered opaque, so only the nearest surface shows. The pending row no longer has `additiveFlame`, so the actor uses the normal render style, and the export manifest records `renderStyle: Normal`. The preview confirmed that style holds.
  - (superseded in round 4) The shader draws a dark amber-smoke body with a strong fullbright fresnel rim, thin painted amber lines along plate edges, and a white-hot axe and visor.
  - (superseded in round 4) Near-black paint (legs, cloak hem) is cut away by a drifting noise threshold, so the legs dissolve into smoke.
  - Light near the floor dims, so the collapsed armour smoulders.
  - The armour is merged into continuous shells: one cuirass, one flared skirt, one tapered sleeve per upper arm and forearm with a single elbow couter, and a tapered thigh, knee cop and greave per leg.
  - The axe, the poses and the amber colour are unchanged.
- **Round 4 (coordinator authority fix):** the opaque ghost read as a wooden mannequin, and Brogue colours the spirit with `spectralImageColor`, the same crimson as the spectral sword. It is now back to translucent additive rendering (`additiveFlame` restored in the pending row, `renderStyle: Add` in the manifest) in the sword's crimson palette.
  - The continuous shells from round 3 are kept.
  - The paint ramps deep crimson, rose, pink and pink-white by value. The axe is a brighter crimson pink-white with a white-hot edge.
  - The shader keeps back-face rejection, a rim-dominant glow with a dim core and the floor-height dimming. The legs and cloak hem fade to black, which is empty when additive.

## Known limitations

- Front-facing overlaps (pauldrons over the chest, arms over the cuirass) still add light, so the interior is quieter but not fully clean.
- The cloak is still a rigid slab from the side.
- The end-of-fade dimming depends on the floor being near world z = 0.
- The fade clip is a collapse of empty armour; bone animation cannot change alpha.
- Brogue's light radius is not visualised by the model.
