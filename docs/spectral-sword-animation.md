# Spectral sword model and animation

Presentation-only BRG-M56 / `MK_SPECTRAL_IMAGE`. Brogue CE remains authoritative.

## Source facts

Pinned `Globals.c` L1139 names catalog kind `MK_SPECTRAL_IMAGE` "spectral sword", with
`spectralImageColor` (13, 0, 0, a dancing red component) and `SPECTRAL_IMAGE_LIGHT`
(`summonedImageLightColor` 200, 0, 75, the "weapon images" light). Flags:
`MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_FLIES`, `MONST_WILL_NOT_USE_STAIRS`,
`MONST_DIES_IF_NEGATED`, `MONST_IMMUNE_TO_WEBS`; 1 HP, attack verb "hits". Prose (L1353):
"Eldritch energies bound up in your equipment have leapt forth to project this spectral
image."

`Combat.c` creates it through the weapon runic `W_MULTIPLICITY`. The wielder's weapon
"emits a flash of light" and `weaponImageCount` duplicates appear as player allies with
a `weaponImageDuration` lifespan. They are renamed "spectral <weapon>", and long names
fall back to "spectral sword/hammer/pike/axe". Separately, armor of multiplicity
(`A_MULTIPLICITY`) clones the attacking monster, sets its ID to `MK_SPECTRAL_IMAGE` and
gives it this colour and light. All of that, including lifespan expiry ("dissipates into
thin air"), stays in Brogue. This model only draws the catalog's spectral sword.

## Art decisions

- A recognisable **hilted broadsword image** about 47 units long, hovering point-down
  with its flat to the camera's +X front. It has a straight double-edged blade, a dark
  see-through fuller with one bright engraved line, a curved crossguard with knobbed
  quillons, an ecusson with a front gem, a wrapped grip, and a wheel pommel with a gem.
  It is crimson with pink-white edges.
- **Projection scanlines** mark it as an image rather than steel. The spectral blade
  uses runes instead.
- **Echoes**: two fainter after-images (paint at 55% and 34% value) sit in **affine
  corner cages** (flame turret technique). They replay the sword's own motion slightly
  late. At idle they fan a few degrees about the guard, giving a doubled, vibrating
  blade. A fast cleave leaves a **fan of three swords**, and a thrust leaves a staggered
  line. This is the "echo" trait, and it is very different from the blue blade's solid
  light crescent.
- It is drawn **additive and fullbright** with the new `shaders/spectral-sword-glow.fp`,
  which adds a crimson rim and a slow projection flicker using renderer time only.

Clips (key pose on the sampled middle frame, odd frame counts):

| Role | Clip | Frames/fps | Middle-frame read |
| --- | --- | --- | --- |
| idle | `idle` | 40 @ 20 loop | point-down hover, sway, echoes shimmer |
| walk | `drift` | 24 @ 24 loop | leans 32°, echoes trail behind |
| attack | `cleave` | 19 @ 35 | diagonal cleave facing the camera: sword horizontal to the right, the two echoes fanned above it |
| attack_alt | `thrust` | 21 @ 35 | full lunge, point at x≈30 near the +X cell limit, echoes staggered behind |
| hit | `recoil` | 13 @ 35 | hilt knocked back 56°, echoes scatter wide |
| death | `fall` | 35 @ 35 | shudder, echoes fling apart and shrink to nothing, sword tips and drops, then clatters and lies flat on the floor, resting on its guard and pommel |

Profile durations `[0, 0, 19, 21, 13, 35]` are 35 Hz tics, each ≥ ceil(frames×35/fps).
There is no `visualScale`.

## Delivered files

- Master: `tools/monster_models/spectral_sword_animation.py`, `spectral_sword_materials.py`;
  tests `tools/monster_models/test_spectral_sword.py`. It imports mesh and pose helpers
  read-only from `spectral_blade_animation.py`, the family module.
- Runtime (new, names collision-checked): `mod/BrogueDoom/models/monsters/56_spectral_image.iqm`
  (named after the existing `56_spectral_image.obj` so the gallery "before" capture
  resolves), `mod/BrogueDoom/graphics/BRGSSWRD.png` (512 atlas),
  `mod/BrogueDoom/shaders/spectral-sword-glow.fp`.
- Editable: `assets/monsters/spectral_sword/spectral-sword-animated.blend`, `animation.json`.
- Pending: `assets/monsters/skeletal_pending/MK_SPECTRAL_IMAGE.json` and `MK_SPECTRAL_IMAGE.gldefs`.

The model has 18 bones (root, sword, 2×8 echo cage corners), 30 source parts (main plus
two echo copies), 4,569 vertices and 7,500 triangles. There is no connected skin.
Weights are quantized to 1e-6 and hold at most 4 influences. Every sampled frame stays
within X/Y −30.8..29.7 and Z 0.48..55.1, with no floor compensation and unit bone
scales.

## Verification (Phase 1)

- Two fresh-process exports gave identical IQM bytes.
- `blender_skeletal.py -- MK_SPECTRAL_IMAGE` built the .blend (exit 0).
- `python -m unittest tools.monster_models.test_spectral_sword`: 10 tests OK.
- Preview galleries (34 captures each, 1920×1080, all capture hashes distinct):
  `artifacts/creature-queue/BRG-M56/preview-vulkan` and `preview-opengl`, contact sheets
  `preview-vulkan-contact.jpg` / `preview-opengl-contact.jpg`. Frozen attempts under
  parallel load were recaptured.

| Asset | SHA256 |
| --- | --- |
| IQM | `a884ddbafdd6e33a0fabfcad1c044e50176ddbcc0b3df428020e9ea43e17ee02` |
| Diffuse | `0a0579ed78e6c8a483b0b10beaa55c9d61187e06c4a71af5899ee98150e71210` |
| Shader | `f876ff953d72fe2cd4531eb61ff4a230821bafa68f2e92d721f29ad79b32557b` |

## Known limitations

- The death middle frame (sword tipping, echoes shrinking away) is fairly thin from the
  oblique camera. The side views are edge-on.
- Because Brogue reuses `MK_SPECTRAL_IMAGE` for armor-of-multiplicity clones of
  arbitrary monsters, a frontend that picks the model only by monster kind would show
  this sword for, say, a spectral goblin. Resolving that would need bridge or display
  work and is outside this presentation-only delivery.
- Integration, shared suites, native build, packaged galleries, natural encounter and
  user art approval remain open.

Original art, CC-BY-SA-4.0; no imports.
