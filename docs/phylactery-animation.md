# Phylactery model and animation

Presentation-only BRG-M41 / `MK_PHYLACTERY` (queue #36). Brogue CE remains authoritative.

## Source facts, art decisions and planned proof

Pinned Brogue (`Globals.c` L1106 catalog, L1300 prose) describes "this gem", the fulcrum of a dark rite that bound the soul of an ancient sorcerer; the player must destroy it before the lich regenerates. The glyph is `G_EGG`, its colour and light are `lichLightColor` (-50, 80, 30: a cold green) and `LICH_LIGHT`, the large flag is false, and it dies as `DF_RUBBLE_BLOOD`. Catalog tokens include `MA_CAST_SUMMON`, `MA_ENTER_SUMMONS`, `MONST_IMMOBILE`, `MONST_INANIMATE`, `MONST_DIES_IF_NEGATED` and `MONST_ALWAYS_HUNTING`; the source summon text is "swirls with dark sorcery as the lich regenerates its form!" and the attack verb is "touches". Lich regeneration, summoning, negation, health, turn timing, visibility, RNG and collision all stay Brogue-owned. The model adds no particles, debris actors or collision.

Art (original interpretation; dimensions are not Brogue facts): an ornate, malevolent soul reliquary. A faceted, elongated lich-green gem is clasped by four thorned claws of antique gilt rising from a dished gilt cup on an octagonal stem. The stem stands on a pale-veined green-black serpentine plinth with proud gilt bands, gripped by four clawed gilt feet (three talons each; the front foot faces the camera). A bone skull boss with slanted deep sockets and a heavy brow sits on the plinth's front. Only the gem is fullbright (a green soul-smoke is painted inside it); everything else is lit normally and painted for flat engine light (alternating facet values, a specular stripe per gilt facet, lit tops and dark lower bands). The gem is the source's glowing "gem"; the skull, claws and gilt are decorative art, not Brogue powers. It is distinct from the goblin and ogre totems (wood, bone, no glow) and from the other three relics.

Gem colour (coordinator review): the gem is the same soul gem the lich carries (`tools/monster_models/lich_materials.py` `GLOW` = 120, 255, 182 and `GLOW_DARK` = 18, 128, 80, keyed fullbright by `shaders/lich-phylactery.fp`; both derive from Brogue's `lichLightColor`). Its facets now use exactly that palette: lit facets burn mint-teal (`GLOW` toward 160, 255, 214), alternate facets stay deep green (`GLOW_DARK` toward 40, 170, 110), with a lighter soul-smoke. Only the gem cell changed; the IQM is byte-identical to the accepted geometry. The lich files were read, not edited.

Earlier self-review passes were rejected: the first export (37 units tall) read too small at 192 units, a flat saturated yellow read as cartoon gold, grime streaks read as wood grain, and the first skull read as a smiley. The final pass is exported ×1.3, uses hard facet contrast and specular stripes, and gives the skull slanted sockets and a brow with no mouth line.

Six roles, with every action key pose on its middle frame:

- `idle` (40 f @ 20 fps, loop): the gem turns ±7° and bobs a fraction of a unit inside the claws;
- `rest` (movement role, 20 f, loop): static — the object has no locomotion;
- `enchant` (attack, 18 f @ 30): the claws bloom outward 44° and the gem rises about 9.8 units and turns 70°, exposing much more fullbright gem above a splayed crown;
- `sorcery` (alternate, 20 f @ 30): the whole upper reliquary leans 17° toward the target (+X), the claws twist into a pinwheel and the gem spins;
- `recoil` (hit, 12 f @ 30): the upper assembly tips back 10° with claw flutter;
- `shatter` (death, 30 f @ 30): the gem jolts, its four quarters burst outward and land around the plinth, the four claws fall outward to lean from the plinth rim to the floor, and the emptied cup topples 64° over the plinth.

Profile durations are engine tics at 35 Hz: `[0, 0, 21, 24, 14, 35]` (= ceil(frames × 35 / fps)). No `visualScale`: the geometry is authored compactly and exported at ×1.3 by the kit.

## Construction

- Generator `tools/monster_models/phylactery_animation.py`, painter `phylactery_materials.py`, shared kit `relic_kit.py`.
- Rigid pieces only (no connected skin, so no cage bake). Ten bones: `root` (plinth, feet, skull), `stem` (cup and knop), `claw_0..3`, `shard_0..3` (gem quarters). Every falling piece is a direct root child so deaths are authored as world-space rigid placements.
- The gem is four closed lathe wedges (two facets each, with planar cut faces) that tile one bipyramid at rest.
- Fullbright key: `mod/BrogueDoom/shaders/phylactery-gem.fp` makes atlas column u ≥ 0.75 (the gem cell only) fullbright. No time, world light, simulation input or RNG.

## Delivered files

- `mod/BrogueDoom/models/monsters/41_phylactery.iqm`, `mod/BrogueDoom/graphics/BRGPHYL.png` (both new names; the static `41_phylactery.obj` and `BRGM41.png` are untouched), `mod/BrogueDoom/shaders/phylactery-gem.fp`.
- `assets/monsters/phylactery/animation.json`, `phylactery-animated.blend`.
- Pending row `assets/monsters/skeletal_pending/MK_PHYLACTERY.json` (report, traits, `ownedFiles` = the shader) and GLDEFS snippet `MK_PHYLACTERY.gldefs`.
- Tests `tools/monster_models/test_phylactery.py`.

## Geometry and bounds

48 rigid parts, 4,647 vertices, 5,144 triangles, 10 bones. Rest dimensions 37.42 / 37.42 / 48.49 units. Across every exported frame X stays within -27.86..27.86, Y within -28.37..28.37 (centred cell ±32), the lowest point is 0.10 (above the 0.07 lift threshold, so no automatic floor compensation) and the highest is 58.29 (below the ~72-unit oblique crop). The final death frame is at most 23.23 high.

## Verification (phase 1)

- Export: `python -m tools.monster_models.phylactery_animation`; a second fresh-process export was byte-identical.

  | File | SHA256 |
  | --- | --- |
  | IQM | `6ea45669adc114f37273e2daaca66aebb0b2d8837a83a9b5c7b144e7b28670c1` |
  | Diffuse | `0f82743d8a3954c4e1e7e522748fb35ac0b4a500000cd697660cd33339946b67` |
  | Shader | `8a1007acf93c626023c1087a28af37629d8da75b7bc798a7cda465e45a03aca5` |
  | `.blend` | `279d022cfaff313ba5c323129ead12bc2d90111230070a4ab5d94b0b82e33d25` |

- No connected skin, so there is no cage bake (rigid single-bone pieces, like the goblin/ogre totems).
- Blender 5.2 background `blender_skeletal.py -- MK_PHYLACTERY` built and freshly reopened the source: 10 bones, 48 parts, all six actions, packed skin, no linked libraries; 18 sampled poses, maximum vertex error 9.88e-06 (`artifacts/creature-queue/BRG-M41/blender-build.log`, `blender-verification.json`).
- Previews: `review_skeletal --symbol MK_PHYLACTERY --preview --all-angles --distances --width 1920 --height 1080` on `--backend 1` and `--backend 0` (`artifacts/creature-queue/BRG-M41/preview-vulkan/`, `preview-opengl/`, contact sheets `preview-vulkan-contact.jpg`, `preview-opengl-contact.jpg`). All 34 stages per backend report `blocking=0`. Gallery hashes (SHA256 of the ordered per-image hashes): Vulkan `e881e20ffa040b24790403599bafedd74ae16e6447cc4d17104c92c8b60fb2c1`, OpenGL `41e79f5abade68bcadb025945fcc56c8080e30215867aede9e480ac3d63332cd`. The only duplicate captures are the expected ones (rest clip, action first/last frames equal to rest, idle mid-loop and front idle/rest where the idle returns to rest); no middle key frame is stale.
- Key captures (Vulkan): front idle `20-idle-0.png`, front attack key `21-enchant-9.png`, oblique attack key `08-enchant-9.png`, final death `18-shatter-29.png`.
- `python -m unittest tools.monster_models.test_phylactery`: 12 tests OK (`tests.log`). Shared checks from `relic_kit.RelicChecks` cover the profile via `skeletal_registry.find` (clips, walk frames, tick durations, no `visualScale`, report, traits, owned shader), the GLDEFS block with fallback to `mod/BrogueDoom/GLDEFS` and a presentation-only shader, rigid single-bone pieces and fullbright-column separation, per-frame ±32 clearance with an unchanged root (no floor lift), loop closure, a static rest clip, unit scales, preserved triangle areas, middle-frame key poses, and exact IQM/texture/manifest bytes; creature-specific tests are listed in the test module.
- Not run (coordinator phase 3): integration, shared suites, native build, packaged galleries, baselines, natural encounter. No user art approval is claimed.

## Shared relic kit

`tools/monster_models/relic_kit.py` is new and is shared only by the four relic creatures (phylactery, eldritch totem, mirrored totem, phoenix egg). It provides lathes (twisted, faceted, wobbled or cut into closed wedge shards), thick `shell()` wedges, swept tubes, extruded bevelled plates, a 4×4 numpy-painted atlas whose column 3 (u ≥ 0.75) is reserved for fullbright keys, world-space rigid placement helpers for floor-settled deaths (`placement`, `lean`, `fall`, `group`), export and manifest writing, and the `RelicChecks` test mixin. It does not modify any shared module.

## Known limitations

- The gem quarters and fallen claws rest on the floor by bounding contact only; slight interpenetration with the plinth's lower tiers and talons is possible, and one shard settles on its edge (up to about 10.6 units high).
- The toppled cup is held by its stem pivot over the plinth rather than resting on a physically solved contact.
- The skull is small; at 128/192 units it reads as a pale boss rather than a detailed skull.
- The gem's facets are painted, not sculpted: because the gem is fullbright, the shader ignores normals.
- The gem uses its own UV-column fullbright key rather than the lich's colour key, so only the palette is shared, not the shader.
