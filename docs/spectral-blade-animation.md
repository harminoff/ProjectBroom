# Spectral blade model and animation

Presentation-only BRG-M55 / `MK_SPECTRAL_BLADE`. Brogue CE remains authoritative.

## Source facts

Pinned `Globals.c` L1137 names it "spectral blade" with `spectralBladeColor`
(15, 15, 60, a dancing blue component) and `SPECTRAL_BLADE_LIGHT`
(`spectralBladeLightColor` 40, 0, 230). Flags: `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`,
`MONST_FLIES`, `MONST_WILL_NOT_USE_STAIRS`, `MONST_DIES_IF_NEGATED`, `MONST_IMMUNE_TO_WEBS`,
`MONST_NOT_LISTED_IN_SIDEBAR`; 1 HP, attack verb "nicks". Prose (L1350): "Eldritch forces
have coalesced to form this flickering, ethereal weapon." Blades are conjured by the
staff of conjuration (`BE_CONJURATION` in `Items.c`, `staffBladeCount`) and summoned as
`HORDE_IS_SUMMONED | HORDE_DIES_ON_LEADER_DEATH` members of the goblin conjurer and the
eldritch totem (`GlobalsBrogue.c` L813, L821). Summoning, flight, negation, leader-bound
death, attacks and timing all stay in Brogue. This model only draws the blade.

## Art decisions

- A **hilt-less, curved, single-edged blade of conjured light**, about 39 units long,
  hovering with its flat to the camera's +X front. It has a white-hot cutting edge and
  point, a violet spine, and a see-through fuller carrying flickering rune dashes. Its
  base is a bright knot with a tilted ring, from which three flame-wisps stream like a
  comet tail, with three motes orbiting the blade. There is no guard, grip or pommel.
  That is the main contrast with the spectral sword, which is a hilted crimson
  broadsword.
- It is drawn **additive and fullbright** (`additiveFlame`, `emissive`) with the new
  `shaders/spectral-blade-glow.fp`. Painted value is opacity, and glancing surfaces gain
  a violet-blue rim. A slow sheen travels up the blade using renderer time only.
- **Presence at distance**: a dim glow envelope hugs each shard. The rim shader turns its
  outline into a soft halo, so the thin blade still reads as a glowing shape at 128/192.
- **Shards**: the blade is built as five jagged, diagonally broken segments with one
  bone each. At rest they meet exactly, and faint crack lines show through the additive
  body.
- **Affine corner cages** (flame turret technique) hold the attack-only light. The slash
  crescent and the whirl ring collapse to zero area outside their key frames, with unit
  bone scales.

Clips (key pose on the sampled middle frame, odd frame counts):

| Role | Clip | Frames/fps | Middle-frame read |
| --- | --- | --- | --- |
| idle | `idle` | 40 @ 20 loop | hover bob, forward lean, wisps wave, motes orbit |
| walk | `drift` | 24 @ 24 loop | leans 40° into travel, wisps stream back |
| attack | `slash` | 19 @ 35 | blade swung out to the right, big blue crescent trail from upper-left (faces the front camera) |
| attack_alt | `whirl` | 21 @ 35 | pinwheel spin toward the camera, inverted blade inside a full ring of light |
| hit | `recoil` | 13 @ 35 | knocked back 52°, shoved and rolled, wisps flung forward |
| death | `shatter` | 35 @ 35 | tremble, then the five shards burst apart at the middle frame, tumble and fall flat on the floor; knot drops, wisps sag onto the floor |

Profile durations `[0, 0, 19, 21, 13, 35]` are 35 Hz tics, each ≥ ceil(frames×35/fps).
There is no `visualScale`.

## Delivered files

- Master: `tools/monster_models/spectral_blade_animation.py`, `spectral_blade_materials.py`;
  tests `tools/monster_models/test_spectral_blade.py`. The blade module also exposes
  its small mesh and pose helpers, which the spectral sword imports read-only.
- Runtime (new, names collision-checked): `mod/BrogueDoom/models/monsters/55_spectral_blade.iqm`,
  `mod/BrogueDoom/graphics/BRGSBLAD.png` (512 atlas), `mod/BrogueDoom/shaders/spectral-blade-glow.fp`.
- Editable: `assets/monsters/spectral_blade/spectral-blade-animated.blend`, `animation.json`.
- Pending: `assets/monsters/skeletal_pending/MK_SPECTRAL_BLADE.json` (`additiveFlame`,
  `emissive`, traits, `ownedFiles` shader) and `MK_SPECTRAL_BLADE.gldefs`.

The model has 38 bones (root, blade, 5 shards, 3×4 wisp chain, 3 motes, 2×8 cage
corners), 20 source parts, 3,028 vertices and 5,172 triangles. There is no connected
skin, so no cage bake. Weights are quantized to 1e-6 with `math.fsum` and hold at most
4 influences. Every sampled frame stays within X/Y −31.6..30.8 and Z 0.2..65.2, with no
automatic floor compensation. The manifest's bind `dimensions` include the attack
trails at their authored key positions.

## Verification (Phase 1)

- Two fresh-process exports gave identical IQM bytes.
- `blender_skeletal.py -- MK_SPECTRAL_BLADE` built the .blend (exit 0).
- `python -m unittest tools.monster_models.test_spectral_blade`: 10 tests OK.
- Preview galleries (34 captures each, 1920×1080, all capture hashes distinct):
  `artifacts/creature-queue/BRG-M55/preview-vulkan` and `preview-opengl`, contact sheets
  `preview-vulkan-contact.jpg` / `preview-opengl-contact.jpg`. Earlier attempts froze
  under parallel load and were recaptured.

| Asset | SHA256 |
| --- | --- |
| IQM | `726f9355a3d33cd946dabb317b5e53f4fd9aaac49d3540352dad295940c55f6c` |
| Diffuse | `f3ce3c9372384a3db18ece08427d54fb58a1d880677250c2ec5cb5ffaae12c2c` |
| Shader | `e23d708d71c32fcc995972056dfb71963887ee20b86522babc114957a6fc79c3` |

## Known limitations

- Seen from the side (±Y gallery views), the blade is edge-on and thin. The wisp tail
  is mostly hidden behind the blade from the exact front.
- The motes are small and barely register beyond 64 units.
- Integration, shared suites, native build, packaged galleries, natural encounter and
  user art approval remain open.

Original art, CC-BY-SA-4.0; no imports.
