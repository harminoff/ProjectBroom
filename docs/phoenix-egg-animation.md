# Phoenix egg model and animation

Presentation-only BRG-M66 / `MK_PHOENIX_EGG` (queue #56). Brogue CE remains authoritative.

## Source facts, art decisions and planned proof

Pinned Brogue (`Globals.c` L1161 catalog, L1386 prose) says: "Cradled in a nest of cooling ashes, the translucent membrane of the phoenix egg reveals a yolk that glows brighter by the second." The glyph is `G_EGG` in `phoenixColor` (red, with a random green component, so red to orange), and it carries `PHOENIX_EGG_LIGHT` (`fireBoltColor`, L970). The large flag is false and it dies as `DF_ASH_BLOOD`. Tokens include `MA_CAST_SUMMON`, `MA_ENTER_SUMMONS`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_NO_POLYMORPH`, `MONST_IMMOBILE` and `MONST_INANIMATE`. The source verb is "cremating" (attack "touches"), and its summon message is "bursts as a newborn phoenix rises from the ashes!" (horde L820 summons one `MK_PHOENIX`). Hatching, the phoenix, fire and weapon immunity, timing, RNG, visibility and collision stay Brogue-owned. The model adds no particles, actors, light or collision.

Art (original interpretation): an ember-cracked egg in a nest of ash. The egg's membrane is fullbright (it has its own light in the source). It is painted dark ember red, lit from within by a hot orange-gold band where the yolk glows through, and carries faint dark capillary veins and a bright yellow-white network of ember cracks, with a bright crack ring around the cap line. A fullbright gold-white yolk and a bright inner lining are sealed inside the shell. The nest is a lumpy, dark-grey heap of cooling ash with soot streaks, a warm glow near the egg and pale dusting. It is crossed by straight charred sticks (chords, not a ring) and splayed sticks, with small fullbright embers on the ash and on some stick tips. Everything is exported ×1.1 so the egg reads at 192 units.

Earlier self-review passes were rejected. A bright smooth mound read as a stone pedestal, a ring of short dark twigs read as a chain, and bright plate seams on a light shell read as a beach ball or wood grain. The final pass darkens and lumps the ash, turns the twigs into crossing chords, darkens the membrane and puts the brightness in the crack network.

Six roles, with every action key pose on its middle frame:

- `idle` (40 f @ 20, loop): the egg rocks gently in a slow circle (3.2°);
- `rest` (movement role, 20 f, loop): static;
- `kindle` (attack, 18 f @ 30): the cap cracks off and lifts about 9.9 units, tilted; the plates part 13° and the glowing yolk rises above the crack line; the egg rocks 5°;
- `bloom` (alternate, 20 f @ 30): the four plates splay 34° like petals around the yolk, with the cap lifted;
- `recoil` (hit, 12 f @ 30): the egg jolts back 9° with plate chatter;
- `burst` (death, 30 f @ 30): the plates are thrown out to lean from the nest rim onto the floor, glowing inner side showing; the cap flips away onto the floor; the yolk sinks out of sight into the ash heap (the newborn phoenix is Brogue's separate creature).

Durations: `[0, 0, 21, 24, 14, 35]` engine tics. No `visualScale`.

## Construction

- Generator `tools/monster_models/phoenix_egg_animation.py`, painter `phoenix_egg_materials.py`, shared `relic_kit.py`.
- Rigid pieces, 7 bones: `root` (nest), `plate_0..3`, `cap`, `yolk`. The shell is built with the kit's thick `shell()` wedges: an outer membrane piece with rim and cut-edge faces, plus a separate inner lining piece scaled toward the egg centre. The yolk is fully inside the lining at rest and fully under the ash surface after death.
- Shader `mod/BrogueDoom/shaders/phoenix-egg-membrane.fp`: atlas column u ≥ 0.75 (membrane, cap, lining, yolk and embers) renders fullbright; ash and sticks are lit. No time, world light, simulation input or RNG.

## Delivered files

- `mod/BrogueDoom/models/monsters/66_phoenix_egg.iqm`, `mod/BrogueDoom/graphics/BRGPHEGG.png` (new names; `66_phoenix_egg.obj`/`BRGM66.png` untouched), `mod/BrogueDoom/shaders/phoenix-egg-membrane.fp`.
- `assets/monsters/phoenix_egg/animation.json`, `phoenix-egg-animated.blend`.
- Pending row `assets/monsters/skeletal_pending/MK_PHOENIX_EGG.json` and `MK_PHOENIX_EGG.gldefs`.
- Tests `tools/monster_models/test_phoenix_egg.py`.

## Geometry and bounds

44 rigid parts, 3,633 vertices, 4,476 triangles, 7 bones. Rest dimensions 39.83 / 38.91 / 32.12 units. Across every exported frame X stays within -26.33..26.11, Y within -26.11..26.11 (centred cell ±32), the lowest point is 0.10 (above the 0.07 lift threshold, so no automatic floor compensation) and the highest is 41.77 (below the ~72-unit oblique crop). The final death frame is at most 10.85 high.

## Verification (phase 1)

- Export: `python -m tools.monster_models.phoenix_egg_animation`; a second fresh-process export was byte-identical.

  | File | SHA256 |
  | --- | --- |
  | IQM | `f790ba917f58c7860f2e9da2f7277ddee3ac0d8682aa41d3b3b2cfb8c4231d65` |
  | Diffuse | `8a2b32634096dd651c3dc6fb6a2edc777ada9951f102f3ded40e4d55b8fce1f3` |
  | Shader | `bdfb3b490f75648afc639f47b1943853646074052190cdba56bba1a2ca798cd1` |
  | `.blend` | `8bf4c4dc9702f8a143d9d87cb6c2d17ee8bc0971909571746f9c3cf5fe889e24` |

- No connected skin, so there is no cage bake (rigid single-bone pieces, like the goblin/ogre totems).
- Blender 5.2 background `blender_skeletal.py -- MK_PHOENIX_EGG` built and freshly reopened the source: 7 bones, 44 parts, all six actions, packed skin, no linked libraries; 18 sampled poses, maximum vertex error 6.08e-06 (`artifacts/creature-queue/BRG-M66/blender-build.log`, `blender-verification.json`).
- Previews: `review_skeletal --symbol MK_PHOENIX_EGG --preview --all-angles --distances --width 1920 --height 1080` on `--backend 1` and `--backend 0` (`artifacts/creature-queue/BRG-M66/preview-vulkan/`, `preview-opengl/`, contact sheets `preview-vulkan-contact.jpg`, `preview-opengl-contact.jpg`). All 34 stages per backend report `blocking=0`. Gallery hashes (SHA256 of the ordered per-image hashes): Vulkan `1914124060a948262af5b0ede945c61562acc3001ca847f3a465636755624956`, OpenGL `3b107642ee8fe7e439fd0b564304937bf866232cce5a3c54ee96b57d01002f41`. The only duplicate captures are the expected ones (rest clip, action first/last frames equal to rest, idle mid-loop and front idle/rest where the idle returns to rest); no middle key frame is stale.
- Key captures (Vulkan): front idle `20-idle-0.png`, front attack key `21-kindle-9.png`, oblique attack key `08-kindle-9.png`, final death `18-burst-29.png`.
- `python -m unittest tools.monster_models.test_phoenix_egg`: 13 tests OK (`tests.log`). Shared checks from `relic_kit.RelicChecks` cover the profile via `skeletal_registry.find` (clips, walk frames, tick durations, no `visualScale`, report, traits, owned shader), the GLDEFS block with fallback to `mod/BrogueDoom/GLDEFS` and a presentation-only shader, rigid single-bone pieces and fullbright-column separation, per-frame ±32 clearance with an unchanged root (no floor lift), loop closure, a static rest clip, unit scales, preserved triangle areas, middle-frame key poses, and exact IQM/texture/manifest bytes; creature-specific tests are listed in the test module.
- Not run (coordinator phase 3): integration, shared suites, native build, packaged galleries, baselines, natural encounter. No user art approval is claimed.

## Shared relic kit

`tools/monster_models/relic_kit.py` is new and is shared only by the four relic creatures (phylactery, eldritch totem, mirrored totem, phoenix egg). It provides lathes (twisted, faceted, wobbled or cut into closed wedge shards), thick `shell()` wedges, swept tubes, extruded bevelled plates, a 4×4 numpy-painted atlas whose column 3 (u ≥ 0.75) is reserved for fullbright keys, world-space rigid placement helpers for floor-settled deaths (`placement`, `lean`, `fall`, `group`), export and manifest writing, and the `RelicChecks` test mixin. It does not modify any shared module.

## Known limitations

- The plate seams are straight meridians and a horizontal cap line, not organic cracks. The painted crack network carries the "ember-cracked" read.
- The nest sticks are simple tubes that interpenetrate each other and the ash heap.
- The burst plates lean by a solved floor contact from a fixed nest-rim point. The cap lands by bounding contact.
- Since the membrane is fullbright, the egg carries no lit shading; its form comes from painted glow bands only.
