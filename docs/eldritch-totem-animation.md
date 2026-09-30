# Eldritch totem model and animation

Presentation-only BRG-M61 / `MK_ELDRITCH_TOTEM` (queue #51). Brogue CE remains authoritative.

## Source facts, art decisions and planned proof

Pinned Brogue (`Globals.c` L1149 catalog, L1368 prose) says: "This totem sits at the center of a summoning circle that radiates a strange energy." The glyph is `G_TOTEM` in `glyphColor` (20, 5, 5 with a random red component: a dark blood red), there is no light, the large flag is false and it dies as `DF_RUBBLE_BLOOD`. Catalog tokens include `MA_CAST_SUMMON`, `MONST_ALWAYS_USE_ABILITY`, `MONST_GETS_TURN_ON_ACTIVATION`, `MONST_IMMOBILE` and `MONST_INANIMATE`; its summon message is "crackles with energy as you touch the glyph!". Its horde rows (`GlobalsBrogue.c` L821–822) summon spectral blades (4–7) and furies (2–3), both dying with the totem. The glyph summoning circle (`DF_GLYPH_CIRCLE`) is Brogue terrain and is not modelled. Summoning, activation, glyph behaviour, timing, RNG, visibility and collision stay Brogue-owned; the model adds no particles, actors or collision.

Art (original interpretation): an alien, unsettling carved spire. A five-sided spire twists about 150° from base to point, built as three stacked, bulging segments and a pointed crown in near-black oxblood stone with pale lavender ridge highlights. Each facet carries glowing red alien glyphs (bars, rings, chevrons, hooks, triangles, dot clusters) in carved dark channels; they are colour-keyed fullbright. Angular horn spurs jut from each segment's upper lip. A dark iron collar carries a ring of five curved single-edged spectral-blue blades that stand up and out around the upper spire; they are fullbright, with pale edges and a dark fuller. The link to the source is that the totem summons spectral blades (blue `spectralBladeColor`); the blades on the model are ornament, not the summoned creatures. A cairn of broken faceted stones buries the foot. A glowing red ichor core is sealed inside each segment top. The design is distinct from the goblin/ogre totems (wood, bone, no glow) and from the other relics.

An earlier pass was rejected in self-review: curling root tendrils plus a pointed top read as a squid, and dense repeated glyphs read as text. The tendrils were replaced by the stone cairn and the glyphs were thinned and varied.

Six roles, with every action key pose on its middle frame:

- `idle` (40 f @ 20, loop): blades sway ±3°, the crown turns ±5°;
- `rest` (movement role, 20 f, loop): static;
- `crackle` (attack, 18 f @ 30): the stacked segments lift apart (4.3 units per joint) and counter-twist, opening three bright red glowing gaps along the spire as the sealed cores slide up to span them; the blade ring swings out flat into a 26-unit horizontal fan and orbits 30°;
- `strike` (alternate, 20 f @ 30): the blades swing round toward the target (+X) and tilt outward, and the spire leans 9° forward with narrower glowing gaps;
- `recoil` (hit, 12 f @ 30): the segments jolt out of line and the spire tips back;
- `topple` (death, 30 f @ 30): the segments and crown break apart and fall outward to lie on the floor, and the blades drop flat, crossed in the gaps. The rooted base and cairn remain as a stump. The cores stay sealed inside their fallen segments.

Durations: `[0, 0, 21, 24, 14, 35]` engine tics. No `visualScale`.

## Construction

- Generator `tools/monster_models/eldritch_totem_animation.py`, painter `eldritch_totem_materials.py`, shared `relic_kit.py`.
- Rigid pieces, 12 bones: `root` (base segment, cairn), `seg1`, `seg2`, `crown`, `core0` (root), `core1` (child of `seg1`), `core2` (child of `seg2`) and `fin_0..4`. Twisted faceted lathes use the kit's per-row twist.
- Shader `mod/BrogueDoom/shaders/eldritch-totem-glyphs.fp`: atlas column u ≥ 0.75 (cores and blades) plus the exact glyph key colour (r ≥ 0.9, g and b ≤ 0.3, painted as `GLYPH` = 255, 40, 30) render fullbright. The painter caps all other stone values below the key, and a test proves key pixels exist only in the stone cell.

## Delivered files

- `mod/BrogueDoom/models/monsters/61_eldritch_totem.iqm`, `mod/BrogueDoom/graphics/BRGELDT.png` (new names; `61_eldritch_totem.obj`/`BRGM61.png` untouched), `mod/BrogueDoom/shaders/eldritch-totem-glyphs.fp`.
- `assets/monsters/eldritch_totem/animation.json`, `eldritch-totem-animated.blend`.
- Pending row `assets/monsters/skeletal_pending/MK_ELDRITCH_TOTEM.json` and `MK_ELDRITCH_TOTEM.gldefs`.
- Tests `tools/monster_models/test_eldritch_totem.py`.

## Geometry and bounds

39 rigid parts, 3,771 vertices, 2,010 triangles, 12 bones. Rest dimensions 27.71 / 28.28 / 57.90 units. Across every exported frame X stays within -28.86..28.56, Y within -28.98..29.14 (centred cell ±32), the lowest point is 0.10 (above the 0.07 lift threshold, so no automatic floor compensation) and the highest is 70.79 (below the ~72-unit oblique crop). The final death frame is at most 16.76 high.

## Verification (phase 1)

- Export: `python -m tools.monster_models.eldritch_totem_animation`; a second fresh-process export was byte-identical.

  | File | SHA256 |
  | --- | --- |
  | IQM | `cdb6c1dd82837c1801e58d35e0ffababccc8006081a3ab07677c82a463bd8757` |
  | Diffuse | `5f4e725458e00bcf00d8bbd5774e08b1d81a836153ee05fff9a5fd8e70333483` |
  | Shader | `1fc4cd5269a9ba9506e874a32ad2e670dcd2390448bc80f3184684f69224a28a` |
  | `.blend` | `5b437cf1e9cabef3f5045f1b7cbc3b7aeaef20934bf0ef074b450cceb3043f5a` |

- No connected skin, so there is no cage bake (rigid single-bone pieces, like the goblin/ogre totems).
- Blender 5.2 background `blender_skeletal.py -- MK_ELDRITCH_TOTEM` built and freshly reopened the source: 12 bones, 39 parts, all six actions, packed skin, no linked libraries; 18 sampled poses, maximum vertex error 8.18e-06 (`artifacts/creature-queue/BRG-M61/blender-build.log`, `blender-verification.json`).
- Previews: `review_skeletal --symbol MK_ELDRITCH_TOTEM --preview --all-angles --distances --width 1920 --height 1080` on `--backend 1` and `--backend 0` (`artifacts/creature-queue/BRG-M61/preview-vulkan/`, `preview-opengl/`, contact sheets `preview-vulkan-contact.jpg`, `preview-opengl-contact.jpg`). All 34 stages per backend report `blocking=0`. Gallery hashes (SHA256 of the ordered per-image hashes): Vulkan `ce470a9f125c69310a39da04c00ec2a4c5dbaf2b65dd7b1ed9d491379c7cfd60`, OpenGL `43961bc57606800a65586692d15d933eaced0049c3b9cdf24a9ec93b4f81a557`. The only duplicate captures are the expected ones (rest clip, action first/last frames equal to rest, idle mid-loop and front idle/rest where the idle returns to rest); no middle key frame is stale.
- Key captures (Vulkan): front idle `20-idle-0.png`, front attack key `21-crackle-9.png`, oblique attack key `08-crackle-9.png`, final death `18-topple-29.png`.
- `python -m unittest tools.monster_models.test_eldritch_totem`: 14 tests OK (`tests.log`). Shared checks from `relic_kit.RelicChecks` cover the profile via `skeletal_registry.find` (clips, walk frames, tick durations, no `visualScale`, report, traits, owned shader), the GLDEFS block with fallback to `mod/BrogueDoom/GLDEFS` and a presentation-only shader, rigid single-bone pieces and fullbright-column separation, per-frame ±32 clearance with an unchanged root (no floor lift), loop closure, a static rest clip, unit scales, preserved triangle areas, middle-frame key poses, and exact IQM/texture/manifest bytes; creature-specific tests are listed in the test module.
- Not run (coordinator phase 3): integration, shared suites, native build, packaged galleries, baselines, natural encounter. No user art approval is claimed.

## Shared relic kit

`tools/monster_models/relic_kit.py` is new and is shared only by the four relic creatures (phylactery, eldritch totem, mirrored totem, phoenix egg). It provides lathes (twisted, faceted, wobbled or cut into closed wedge shards), thick `shell()` wedges, swept tubes, extruded bevelled plates, a 4×4 numpy-painted atlas whose column 3 (u ≥ 0.75) is reserved for fullbright keys, world-space rigid placement helpers for floor-settled deaths (`placement`, `lean`, `fall`, `group`), export and manifest writing, and the `RelicChecks` test mixin. It does not modify any shared module.

## Known limitations

- The glyphs are procedural shapes, not an alphabet. At 192 units they merge into red specks, and the blades and gap glow carry the read.
- The spire is five-sided and low-poly by design; its close views show hard facets.
- The fallen segments lie by bounding contact and can interpenetrate the cairn stones slightly.
- The summoning-circle floor glyphs are Brogue terrain and are not shown by this model.
