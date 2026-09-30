# Mirrored totem model and animation

Presentation-only BRG-M62 / `MK_MIRRORED_TOTEM` (queue #52). Brogue CE remains authoritative.

## Source facts, art decisions and planned proof

Pinned Brogue (`Globals.c` L1151 catalog, L1373 prose) says: "A prism of shoulder-high mirrored surfaces gleams in the darkness." The glyph is `G_TOTEM` in `beckonColor` (10, 10, 10: near black), with no light; the large flag is false and it dies as `DF_RUBBLE_BLOOD`. Its catalog carries `MA_REFLECT_100`, the bolt `BOLT_BECKONING`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMOBILE` and `MONST_INANIMATE`, and a 100% `DF_MIRROR_TOTEM_STEP` feature whose message (L730) is "the mirrored totem flashes, reflecting the red glow of the glyph beneath you." The pinned source gives it beckoning and reflection. It does not create mirror images; the handoff brief's "mirror images" wording is not reflected in the source and is not modelled. Reflection, beckoning, glyph reactions, weapon/fire immunity, timing, RNG, visibility and collision stay Brogue-owned. The model adds no particles, actors or collision.

Art (original interpretation), second pass after coordinator review: the first pass read as a clear glass display case or lantern (a bright box on a plinth). The prism, plinth, crown, flash crystal and hinge/flash/shatter clips are kept, but:

- The panels now read as opaque polished mirror, not glass. Each face has its own painted atlas cell (`mirror_0..2`, crown shards `mirror_3`) with reflected-environment banding: a dark cave/floor reflection in the lower part, a bright horizon streak at a different height on each face, a pale secondary band, then darker cool upper reflections falling into a dark vault, with soft reflected pillars and wall blocks, two or three angled highlight streaks at per-face angles, and a dark bevel. The shader keeps a small view-dependent term and 0.3 fullbright, but the painted base dominates. There is no see-through read.
- Totem character: a heavier engraved pewter frame (thick foot and head rails, stiles, silver bosses top and bottom), three engraved pewter corner columns with silver knops at the prism edges, and a taller three-step carved plinth (12 units) with recessed panels, pale engraved borders and three pewter bands.
- A distinctive crown: a pewter triangular crown carries a ring of six small angled mirror shards around a tall faceted mirror finial. The silhouette is no longer a plain box.
- Separation from the grey walls comes from cool silver highlights, bright horizon streaks and pale bosses against the dark blue-black lacquer and dark mirror.

The prism is 32 units of mirror on a 12-unit plinth (the mirrored surfaces are about shoulder height); the finial tops out at 57 units. One prism edge faces the camera, so two mirrors angle toward the viewer. A fullbright white-gold flash crystal (three crossed diamonds) is sealed inside the closed prism; it is the visible "flash". The near-black `beckonColor` is an identity cue only.

Six roles, with every action key pose on its middle frame:

- `idle` (40 f @ 20, loop): the crown turns ±4°;
- `rest` (movement role, 20 f, loop): static;
- `flash` (attack, 18 f @ 30): all three panels hinge open 31° at their feet between the standing columns, the crown lifts 11 units and tilts, and the flash crystal rises above the panel tops;
- `beckon` (alternate, 20 f @ 30): the two camera-facing mirrors lower 50° toward the target, the back panel opens 10°, and the crystal rises to show through the opening;
- `recoil` (hit, 12 f @ 30): the panels shiver and the crown jolts;
- `shatter` (death, 30 f @ 30): the lower panel pieces fall flat outward onto the floor, the cracked upper pieces collapse in a stacked heap on the plinth, the corner columns snap and lie flat between the fallen panels, the crown topples onto the fallen rear mirror, and the flash crystal lies down sealed inside the plinth.

Durations: `[0, 0, 21, 24, 14, 35]` engine tics. No `visualScale`.

## Construction

- Generator `tools/monster_models/mirrored_totem_animation.py`, painter `mirrored_totem_materials.py`, shared `relic_kit.py`.
- Rigid pieces, 12 bones: `root` (plinth), `panel_0..2` (lower mirror piece, foot rail, lower stiles, foot boss), `shard_0..2` (upper mirror piece, head rail, upper stiles, head boss), `column_0..2`, `cap` and `flash`. Both halves of a panel share its bottom hinge pivot and receive the same rotation in every non-death clip, so the panel stays whole until it shatters. Both halves share one UV box, so the painted mirror is continuous across the crack.
- Shader `mod/BrogueDoom/shaders/mirrored-totem-mirror.fp`: the mirror cells (0.5 ≤ u < 0.75) keep the painted base, modulated by a fake vault/horizon/floor environment at 0.3 fullbright; the flash cell (u ≥ 0.75) is fullbright. Its only input is the camera position: no time, world light, simulation state or RNG.

## Delivered files

- `mod/BrogueDoom/models/monsters/62_mirrored_totem.iqm`, `mod/BrogueDoom/graphics/BRGMIRT.png` (new names; `62_mirrored_totem.obj`/`BRGM62.png` untouched), `mod/BrogueDoom/shaders/mirrored-totem-mirror.fp`.
- `assets/monsters/mirrored_totem/animation.json`, `mirrored-totem-animated.blend`.
- Pending row `assets/monsters/skeletal_pending/MK_MIRRORED_TOTEM.json` and `MK_MIRRORED_TOTEM.gldefs`.
- Tests `tools/monster_models/test_mirrored_totem.py`.

## Geometry and bounds

56 rigid parts, 4,050 vertices, 1,726 triangles, 12 bones. Rest dimensions 26.15 / 30.20 / 56.90 units. Across every exported frame X stays within -30.80..23.15, Y within -30.32..30.32 (centred cell ±32), the lowest point is 0.10 (above the 0.07 lift threshold, so no automatic floor compensation) and the highest is 67.71 (below the ~72-unit oblique crop). The final death frame is at most 23.22 high (the crown lying on its side).

## Verification (phase 1)

- Export: `python -m tools.monster_models.mirrored_totem_animation`; a second fresh-process export was byte-identical.

  | File | SHA256 |
  | --- | --- |
  | IQM | `d63374fb119d487a4c70c5425de94382f380777cf5380bb7a8067da46c21f846` |
  | Diffuse | `b9ed461d3f422a0c2bf99218e27349d2d009895775bb7dcb3345d2f8066015e0` |
  | Shader | `56375399f74119daeed542b80096546ca5e9f79c9ae2db1782ce5505dc5f5bd6` |
  | `.blend` | `e346d2c136d856fa01df268c06e0ac073cf8bedff82897388d65a4f55b0c24dc` |

- No connected skin, so there is no cage bake (rigid single-bone pieces, like the goblin/ogre totems).
- Blender 5.2 background `blender_skeletal.py -- MK_MIRRORED_TOTEM` built and freshly reopened the source: 12 bones, 56 parts, all six actions, packed skin, no linked libraries; 18 sampled poses, maximum vertex error 1.04e-05 (`artifacts/creature-queue/BRG-M62/blender-build.log`, `blender-verification.json`).
- Previews: `review_skeletal --symbol MK_MIRRORED_TOTEM --preview --all-angles --distances --width 1920 --height 1080` on `--backend 1` and `--backend 0` (`artifacts/creature-queue/BRG-M62/preview-vulkan/`, `preview-opengl/`, contact sheets `preview-vulkan-contact.jpg`, `preview-opengl-contact.jpg`). All 34 stages per backend report `blocking=0`. Gallery hashes (SHA256 of the ordered per-image hashes): Vulkan `055386b85820f57e9f54a97d50ad65868c7fa086387937071db4fde63d48f5ab`, OpenGL `b1277750d4ba401385aa172b0c09507bb24f4b33c925c956fefe6a0bfe215521`. The only duplicate captures are the expected ones (rest clip, action first/last frames equal to rest, idle mid-loop and front idle/rest where the idle returns to rest); no middle key frame is stale.
- Key captures (Vulkan): front idle `20-idle-0.png`, front attack key `21-flash-9.png`, oblique attack key `08-flash-9.png`, final death `18-shatter-29.png`.
- `python -m unittest tools.monster_models.test_mirrored_totem`: 13 tests OK (`tests.log`). Shared checks from `relic_kit.RelicChecks` cover the profile via `skeletal_registry.find` (clips, walk frames, tick durations, no `visualScale`, report, traits, owned shader), the GLDEFS block with fallback to `mod/BrogueDoom/GLDEFS` and a presentation-only shader, rigid single-bone pieces and fullbright-column separation, per-frame ±32 clearance with an unchanged root (no floor lift), loop closure, a static rest clip, unit scales, preserved triangle areas, middle-frame key poses, and exact IQM/texture/manifest bytes; creature-specific tests are listed in the test module.
- Not run (coordinator phase 3): integration, shared suites, native build, packaged galleries, baselines, natural encounter. No user art approval is claimed.

## Shared relic kit

`tools/monster_models/relic_kit.py` is new and is shared only by the four relic creatures (phylactery, eldritch totem, mirrored totem, phoenix egg). It provides lathes (twisted, faceted, wobbled or cut into closed wedge shards), thick `shell()` wedges, swept tubes, extruded bevelled plates, a 4×4 numpy-painted atlas whose column 3 (u ≥ 0.75) is reserved for fullbright keys, world-space rigid placement helpers for floor-settled deaths (`placement`, `lean`, `fall`, `group`), export and manifest writing, and the `RelicChecks` test mixin. It does not modify any shared module.

## Known limitations

- The reflection is painted banding plus a fake environment term, not a true reflection of the room or the player. The mirrors are fairly dark overall; at 192 units the read comes from the horizon streaks, the silver frame and the crown.
- The crack line between the two halves of each panel is a hidden seam at rest. A hairline may show at extreme close range.
- In the death heap, the shards are stacked at fixed heights over the plinth, and some edges overhang in the air.
- The source has no "mirror images"; only reflection, beckoning and the flash are represented.
- The beckon key pose reaches Y ±30.3 and the death reaches X -30.8, inside the ±32 cell limit.
- Fallen columns, panels and the crown lie by bounding contact and can overlap slightly; the crown rests on the rear panel at a fixed height.
